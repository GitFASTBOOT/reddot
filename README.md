# TWRP Builder Bot

A Telegram bot for automating TWRP (Team Win Recovery Project) image builds directly from a chat interface. Users can queue build jobs, monitor progress, and receive built artifacts (recovery, boot, and vendor\_boot images) via Telegram.

---

## Table of Contents

* [Features](#features)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Configuration](#configuration)
* [Running the Bot](#running-the-bot)
* [Bot Commands](#bot-commands)
* [Build Workflow](#build-workflow)
* [Queue Management](#queue-management)
* [Advanced Tips](#advanced-tips)
* [Troubleshooting](#troubleshooting)
* [Contributing](#contributing)
* [License](#license)

---

## Features

* 🛠️ **Automated builds**: Clone device trees and build TWRP images for any supported device.
* 📥 **Queue system**: Multiple users can queue jobs; builds process sequentially.
* 🔧 **Live logs**: Periodic updates on build progress straight to your chat.
* 📤 **Artifact delivery**: Receives compiled `.img` or `.img.gz` files up to Telegram’s 50 MB limit.
* 🚦 **Admin controls**: Manage queue (move, clear) and cancel jobs globally.

---

## Prerequisites

1. **Server** or machine with:

   * Linux environment (Ubuntu, Debian, etc.)
   * Bash shell
   * [Android build environment](https://source.android.com/docs/setup/build/requirements) for TWRP 12.1
2. **System packages**:

   ```bash
   sudo apt update && sudo apt install -y git python3 python3-venv python3-pip gzip
   ```
3. **Telegram Bot Token**: Obtain from [@BotFather](https://t.me/BotFather).
4. **Admin Telegram IDs**: Numeric user IDs of bot administrators.
5. **PushListener** (optional): A Telegram user or group to receive notifications.

---

## Installation

1. **Clone this repository**:

   ```bash
   git clone https://github.com/GitFASTBOOT/reddot.git
   cd reddot
   ```

2. **Create a Python virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install --upgrade pip
   pip install python-telegram-bot
   ```

4. **Prepare Android build tree**:

   * Clone or set up your Android source under the path defined in `FULL_ANDROID_PATH`.
   * Ensure `build/envsetup.sh` is present and functional.

---

## Configuration

Open `src/config.py` and locate the **Configuration** section near the top:

```python
ALLOWED_TARGETS = ["recovery", "boot", "vendor_boot"]
TARGET_MAPPING = {
    "recovery": "recoveryimage",
    "boot": "bootimage",
    "vendor_boot": "vendorbootimage",
}
ADMIN_IDS = [123456789]         # Replace with your Telegram user ID(s)
TOKEN = "<YOUR_BOT_TOKEN>"   # Replace with your BotFather token
FULL_ANDROID_PATH = "/sdb/build/twrp12.1"  # Path to your Android source root
```

* **ALLOWED\_TARGETS**: Valid build targets accepted by `/build`.
* **TARGET\_MAPPING**: Maps friendly names to the make targets.
* **ADMIN\_IDS**: List of Telegram user IDs allowed to manage the queue.
* **TOKEN**: Bot token string.
* **FULL\_ANDROID\_PATH**: Absolute path to Android build root (where `build/envsetup.sh` lives).

---

## Running the Bot

Activate your virtual environment (if not already):

```bash
source venv/bin/activate
```

Start the bot:

```bash
python main.py
```

You should see logs indicating the bot is polling for updates:

```
INFO - Starting bot...
```

---

## Bot Commands

### User Commands

| Command                                       | Description                                                                     |
| --------------------------------------------- | ------------------------------------------------------------------------------- |
| `/start`                                      | Show welcome message and usage summary.                                         |
| `/build <repo> <path> <target1> [target2...]` | Queue a build job. E.g.: `/build https://github.com/... lavender recovery boot` |
| `/queue`                                      | Display the current build queue.                                                |
| `/cancel <position>`                          | Cancel *your* queued job at the given position.                                 |
| `/logs`                                       | Show the last 5 lines of active build logs.                                     |

### Admin Commands

| Command             | Description                              |
| ------------------- | ---------------------------------------- |
| `/move <from> <to>` | Move a job from one position to another. |
| `/clearqueue`       | Clear all jobs from the queue.           |

---

## Build Workflow

1. **Queueing**: A user invokes `/build` with a Git repo, device path, and target(s).
2. **Cloning**: Bot cleans previous device folder entries, clones the specified repo to `<FULL_ANDROID_PATH>/device/<path>`.
3. **Building**:

   * Sources environment: `. build/envsetup.sh && breakfast <codename>`
   * Runs `mka <make-targets>` for recovery, boot, vendor\_boot images.
   * Streams logs every 15 seconds (configurable).
4. **Artifact Delivery**: On success, bot uploads artifacts under `out/target/product/<codename>/`.

   * If any file >50 MB, it is gzipped and then uploaded (if <50 MB after compression).

---

## Queue Management

* **Sequential Processing**: Only one build runs at a time.
* **Position Reporting**: Users see their queue position when enqueuing.
* **Cancellation**: Users can remove their own jobs; admins can clear or reorder.

---

## Advanced Tips

* **Custom Targets**: Extend `ALLOWED_TARGETS` and `TARGET_MAPPING` for extra build variants.
* **Timeouts**: Adjust `timeout` in clone and shell subprocess calls if your builds take longer.
* **Log Buffer**: Modify `LOG_BUFFER_SIZE` and `LOG_UPDATE_INTERVAL` for more or fewer log updates.
* **Error Handling**: Check `logs` for `RetryAfter` or network errors during heavy loads.

---

## Troubleshooting

* **Clone failures**: Ensure the repo URL is valid and accessible from the server.
* **Build errors**: Check Android build logs locally first (run commands manually).
* **Permission issues**: Verify file system permissions under `FULL_ANDROID_PATH`.
* **Flood control**: Bot auto-retries after backoff; reduce message frequency if hitting limits.

---

## Contributing

Contributions are welcome! Feel free to open issues or pull requests for:

* Supporting additional build targets
* Improved error reporting
* Containerized deployments (Docker)

---

## License

This project is licensed under the [MIT License](LICENSE).
