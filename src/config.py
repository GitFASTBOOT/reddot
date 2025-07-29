import os

# Bot configuration
ALLOWED_TARGETS = ["recovery", "boot", "vendor_boot"]
TARGET_MAPPING = {
    "recovery": "recoveryimage",
    "boot": "bootimage",
    "vendor_boot": "vendorbootimage",
}
ADMIN_IDS = [123456789]
TOKEN = ""
FULL_ANDROID_PATH = ""

# Logging and buffer settings
LOG_BUFFER_SIZE = 100
LOG_UPDATE_INTERVAL = 15

