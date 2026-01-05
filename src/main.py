from handlers.menus.main import closest_stop_handler
from handlers.error_handler import error_handler
from services.bus_stop import BusStopService
from services.admin import AdminService
from loguru import logger
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import settings
from database.database import init_db
from handlers.menus.main import (
    BusesMenuAnswers,
    ConversationStep,
    MainMenuAnswers,
    StopsMenuAnswers,
    add_stop_code,
    add_stop_location,
    add_stop_name,
    buses_menu_handler,
    cancel,
    main_menu_handler,
    start_main_menu,
    stops_menu_handler,
)
from handlers.start_handler import start_handler
from services.user import UserService



if __name__ == "__main__":
    init_db()

    app = ApplicationBuilder().token(settings.telegram_token).build()
    logger.info("Application built")

    app.bot_data["user_service"] = UserService()
    app.bot_data["admin_service"] = AdminService()
    app.bot_data["bus_stop_service"] = BusStopService()


    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("menu", start_main_menu)],
        states={
            ConversationStep.MAINMENU: [CallbackQueryHandler(main_menu_handler, pattern=f"^({"|".join([option.value for option in MainMenuAnswers])})$")],
            ConversationStep.BUSES: [CallbackQueryHandler(buses_menu_handler, pattern=f"^({"|".join([option.value for option in BusesMenuAnswers])})$")],
            ConversationStep.STOPS: [CallbackQueryHandler(stops_menu_handler, pattern=f"^({"|".join([option.value for option in StopsMenuAnswers])})$")],
            ConversationStep.ADD_STOP: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_stop_code)],
            ConversationStep.ADD_STOP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_stop_name)],
            ConversationStep.ADD_STOP_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND | filters.LOCATION, add_stop_location)],
            ConversationStep.GET_CLOSEST: [MessageHandler(filters.TEXT & ~filters.COMMAND | filters.LOCATION, closest_stop_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
        per_user=True,
        per_message=False
    ))
    app.add_error_handler(error_handler)


    logger.info("Starting polling")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
