import sys
import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler

# Path settings
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import components
from config import TOKEN
from handlers import (
    start, build, logs, queue_list, cancel_job,
    move_job, clear_queue, error_handler
)

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Correct coroutine for post_init
async def on_startup(app):
    logging.info("Bot initialized.")

def main():
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(on_startup)
        .write_timeout(30)
        .build()
    )

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("build", build))
    application.add_handler(CommandHandler("logs", logs))
    application.add_handler(CommandHandler("queue", queue_list))
    application.add_handler(CommandHandler("cancel", cancel_job))
    application.add_handler(CommandHandler("move", move_job))
    application.add_handler(CommandHandler("clearqueue", clear_queue))
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
