from typing import Optional
from loguru import logger
from telegram.ext import CallbackContext

async def error_handler(update: Optional[object], context: CallbackContext) -> None:
    """Log errors."""
    logger.warning(f'Update {update} caused error {context.error}')
