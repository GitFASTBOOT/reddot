import os
import subprocess
import shutil
import time
import asyncio

from telegram.ext import ContextTypes
from config import FULL_ANDROID_PATH, TARGET_MAPPING, LOG_BUFFER_SIZE, LOG_UPDATE_INTERVAL
from state import BUILD_QUEUE, BUILD_IN_PROGRESS, CURRENT_LOGS
from utils import safe_send

async def process_build_queue(context: ContextTypes.DEFAULT_TYPE):
    """
    Process build jobs sequentially.
    """
    global BUILD_IN_PROGRESS, BUILD_QUEUE, CURRENT_LOGS
    BUILD_IN_PROGRESS = True

    while BUILD_QUEUE:
        user_id, repo_url, device_path, targets = BUILD_QUEUE.pop(0)
        CURRENT_LOGS.clear()
        device_path_full = os.path.join(FULL_ANDROID_PATH, 'device', *device_path.split('/'))

        # Notify and prepare
        await safe_send(context, user_id, f"🧹 Cleaning for {os.path.basename(repo_url)}...")
        shutil.rmtree(os.path.join(FULL_ANDROID_PATH, 'out'), ignore_errors=True)
        if os.path.exists(device_path_full):
            shutil.rmtree(device_path_full, ignore_errors=True)

        # Clone repo
        await safe_send(context, user_id, f"⚙️ Cloning {repo_url}...")
        result = subprocess.run(
            ["git", "clone", "--depth=1", repo_url, device_path_full],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            await safe_send(context, user_id, f"❌ Clone failed: {result.stderr[:200]}")
            continue

        # Setup build env and start build
        codename = os.path.basename(device_path)
        await safe_send(context, user_id, f"🔨 Building targets: {', '.join(targets)}")
        bash_cmd = (
            f". build/envsetup.sh && breakfast {codename} && "
            f"mka {' '.join(TARGET_MAPPING[t] for t in targets)}"
        )
        proc = await asyncio.create_subprocess_shell(
            bash_cmd,
            cwd=FULL_ANDROID_PATH,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            executable='/bin/bash'
        )

        last_update = time.time()
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            log = line.decode().strip()
            CURRENT_LOGS.append(log)
            if len(CURRENT_LOGS) > LOG_BUFFER_SIZE:
                CURRENT_LOGS.pop(0)
            if time.time() - last_update > LOG_UPDATE_INTERVAL:
                snippet = "\n".join(CURRENT_LOGS[-5:])
                await safe_send(context, user_id, f"```\n{snippet}\n```")
                last_update = time.time()

        await proc.wait()
        if proc.returncode != 0:
            await safe_send(context, user_id, "❌ Build failed. Check logs.")
            continue

        # Send artifacts
        out_dir = os.path.join(FULL_ANDROID_PATH, 'out', 'target', 'product', codename)
        for t in targets:
            img_name = f"{t}.img"
            img_path = os.path.join(out_dir, img_name)
            if not os.path.exists(img_path):
                continue
            # Compress if too large (over 48 MB)
            size_mb = os.path.getsize(img_path) / (1024 * 1024)
            if size_mb > 48:
                gz_path = f"{img_path}.gz"
                subprocess.run(["gzip", "-k", img_path], check=True)
                img_path = gz_path
            await context.bot.send_document(chat_id=user_id, document=open(img_path, 'rb'))

        await safe_send(context, user_id, "✅ Build completed!")

    BUILD_IN_PROGRESS = False

