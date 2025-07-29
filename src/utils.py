import asyncio
import logging
from telegram.ext import ContextTypes
from telegram.error import RetryAfter

logger = logging.getLogger(__name__)

async def safe_send(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str, retry_count: int = 0):
    """
    Send a message with retry logic for flood control.
    """
    try:
        await context.bot.send_message(chat_id=chat_id, text=text)
    except RetryAfter as e:
        if retry_count > 3:
            logger.warning(f"Failed after 3 retries: {text}")
            return
        wait = e.retry_after + 2
        logger.info(f"Flood control: Waiting {wait}s")
        await asyncio.sleep(wait)
        await safe_send(context, chat_id, text, retry_count + 1)
    except Exception as e:
        logger.error(f"Send failed: {str(e)}")

