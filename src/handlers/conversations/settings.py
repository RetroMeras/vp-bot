from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, BaseHandler, CommandHandler

def get_settings_conversation_handler() -> BaseHandler:
    return CommandHandler("settings", news_handler)

async def news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return None

    await update.message.reply_text("Настройки в разработке", reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")