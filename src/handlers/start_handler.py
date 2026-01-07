from services import Services
from telegram import ReplyKeyboardMarkup
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return None

    services: Services = context.bot_data["services"]
    services.user.add_or_update_user(update.effective_user)
    logger.info(f"Started for user {update.effective_user.username}")

    await update.message.reply_text(
        f"Добрый день, {update.effective_user.first_name}!",
        reply_markup=ReplyKeyboardMarkup([
            ["/buses", "/news"],
            ["/about", "/settings"],
        ], resize_keyboard=True),
        parse_mode="Markdown"
    )
