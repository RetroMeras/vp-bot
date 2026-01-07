from services import create_services
from handlers.conversations.settings import get_settings_conversation_handler
from handlers.conversations.about import get_about_conversation_handler
from handlers.conversations.news import get_news_conversation_handler
from handlers.conversations.buses import get_buses_conversation_handler
from handlers.error_handler import error_handler
from loguru import logger
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

from config import settings
from database.database import init_db
from handlers.start_handler import start_handler


if __name__ == "__main__":
    init_db()

    app = ApplicationBuilder().token(settings.telegram_token).build()
    logger.info("Application built")


    app.bot_data["services"] = create_services()


    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(get_buses_conversation_handler())
    app.add_handler(get_news_conversation_handler())
    app.add_handler(get_about_conversation_handler())
    app.add_handler(get_settings_conversation_handler())
    app.add_error_handler(error_handler)


    logger.info("Starting polling")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
