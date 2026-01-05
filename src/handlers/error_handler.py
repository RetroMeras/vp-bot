from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.warning(f'Update {update} caused error {context.error}')
