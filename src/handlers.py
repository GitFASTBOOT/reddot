import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import ALLOWED_TARGETS, ADMIN_IDS
from state import BUILD_QUEUE, CURRENT_LOGS
from utils import safe_send
from build_manager import process_build_queue

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command: send help and usage information.
    """
    usage = (
        "🚀 TWRP Builder Bot\n\n"
        "📚 Usage:\n/build <repo> <path> <targets>\n\n"
        "⚙️ Queue Management:\n"
        "/queue - Show current queue\n"
        "/cancel <position> - Cancel your job\n"
    )
    await safe_send(context, update.effective_chat.id, usage)

async def build(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /build command: validate input and enqueue build job.
    """
    args = context.args
    if len(args) < 3:
        await safe_send(context, update.effective_chat.id,
                        "❌ Format: /build <repo> <path> <target1> [target2...]")
        return

    repo_url, device_path, targets = args[0], args[1], args[2:]
    user_id = update.message.from_user.id

    # Validate inputs
    if not (repo_url.startswith("https://github.com/") and ".." not in device_path):
        await safe_send(context, user_id, "❌ Invalid input")
        return

    invalid_targets = [t for t in targets if t not in ALLOWED_TARGETS]
    if invalid_targets:
        await safe_send(context, user_id,
                        f"❌ Invalid targets: {', '.join(invalid_targets)}")
        return

    BUILD_QUEUE.append((user_id, repo_url, device_path, targets))
    position_msg = f"📅 Queued! Position: {len(BUILD_QUEUE)}"
    await safe_send(context, user_id, position_msg)

    from state import BUILD_IN_PROGRESS
    if not BUILD_IN_PROGRESS:
        await process_build_queue(context)

async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /logs command: show recent build logs.
    """
    if not CURRENT_LOGS:
        await safe_send(context, update.effective_chat.id, "📭 No logs available.")
        return
    logs_snippet = "\n".join(CURRENT_LOGS[-10:])
    await safe_send(context, update.effective_chat.id, f"```\n{logs_snippet}\n```")

async def queue_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /queue: list current build queue.
    """
    if not BUILD_QUEUE:
        await safe_send(context, update.effective_chat.id, "📭 The queue is empty.")
        return
    msg = "📋 Current Queue:\n"
    for idx, (uid, repo, path, _) in enumerate(BUILD_QUEUE, 1):
        msg += f"{idx}. {repo} ({path})\n"
    await safe_send(context, update.effective_chat.id, msg)

async def cancel_job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /cancel: remove a user's job from the queue.
    """
    args = context.args
    if len(args) != 1 or not args[0].isdigit():
        await safe_send(context, update.effective_chat.id, "❌ Use: /cancel <position>")
        return
    pos = int(args[0])
    user_id = update.message.from_user.id
    if pos < 1 or pos > len(BUILD_QUEUE):
        await safe_send(context, user_id, "❌ Invalid position.")
        return
    if BUILD_QUEUE[pos - 1][0] != user_id:
        await safe_send(context, user_id, "❌ You can only cancel your own jobs.")
        return
    BUILD_QUEUE.pop(pos - 1)
    await safe_send(context, user_id, f"🗑️ Canceled job at position {pos}.")

async def move_job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /move: admin reorders the queue.
    """
    if update.message.from_user.id not in ADMIN_IDS:
        await safe_send(context, update.effective_chat.id, "❌ Unauthorized.")
        return
    args = context.args
    if len(args) != 2 or not all(arg.isdigit() for arg in args):
        await safe_send(context, update.effective_chat.id, "❌ Use: /move <from> <to>")
        return
    frm, to = map(int, args)
    if min(frm, to) < 1 or max(frm, to) > len(BUILD_QUEUE):
        await safe_send(context, update.effective_chat.id, "❌ Invalid positions.")
        return
    job = BUILD_QUEUE.pop(frm - 1)
    BUILD_QUEUE.insert(to - 1, job)
    await safe_send(context, update.effective_chat.id, f"🔀 Moved job from {frm} to {to}.")

async def clear_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /clearqueue: admin clears all jobs.
    """
    if update.message.from_user.id not in ADMIN_IDS:
        await safe_send(context, update.effective_chat.id, "❌ Unauthorized.")
        return
    BUILD_QUEUE.clear()
    await safe_send(context, update.effective_chat.id, "🗑️ Queue cleared.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Global error handler.
    """
    logger = logging.getLogger(__name__)
    logger.error(f"Exception: {context.error}")
    await safe_send(context, update.effective_chat.id,
                    "⚠️ An error occurred. Please try again later.")

