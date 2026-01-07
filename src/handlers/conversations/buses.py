from handlers.conversations.buses_utils.route_handlers import handle_routes_csv_upload
from handlers.conversations.buses_utils.route_handlers import routes_menu_handler
from handlers.conversations.buses_utils.enums import RoutesMenuAnswers
from handlers.conversations.buses_utils.csv_handlers import handle_csv_upload
from handlers.conversations.buses_utils.location_handlers import closest_stop_handler
from handlers.conversations.buses_utils.add_stops_handlers import add_stop_location
from handlers.conversations.buses_utils.add_stops_handlers import add_stop_name
from handlers.conversations.buses_utils.add_stops_handlers import add_stop_code
from handlers.conversations.buses_utils.stops_handler import stops_menu_handler
from handlers.conversations.buses_utils.bus_menu_handlers import buses_menu_handler
from handlers.conversations.buses_utils.bus_menu_handlers import buses_menu
from handlers.conversations.buses_utils.enums import StopsMenuAnswers, BusesMenuAnswers, BusesConversationSteps
from handlers.conversations.buses_utils.data_manager import UserDataManager
from handlers.cancel_handler import cancel
from telegram.ext import ConversationHandler, BaseHandler, CallbackQueryHandler, CommandHandler, MessageHandler, filters

user_data_manager = UserDataManager()

def get_buses_conversation_handler() -> BaseHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("buses", buses_menu)],
        states={
            BusesConversationSteps.BUSES: [CallbackQueryHandler(buses_menu_handler, pattern=f"^({'|'.join([option for option in BusesMenuAnswers])})$")],
            BusesConversationSteps.STOPS: [CallbackQueryHandler(stops_menu_handler, pattern=f"^({'|'.join([option for option in StopsMenuAnswers])})$")],
            BusesConversationSteps.ADD_STOP: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_stop_code)],
            BusesConversationSteps.ADD_STOP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_stop_name)],
            BusesConversationSteps.ADD_STOP_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND | filters.LOCATION, add_stop_location)],
            BusesConversationSteps.GET_CLOSEST: [MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.LOCATION, closest_stop_handler)],
            BusesConversationSteps.CSV_UPLOAD: [MessageHandler(filters.Document.ALL, handle_csv_upload)],
            BusesConversationSteps.ROUTES: [
                CallbackQueryHandler(routes_menu_handler,
                    pattern=f"^({'|'.join([option for option in RoutesMenuAnswers])})$")
            ],
            BusesConversationSteps.ROUTES_CSV_UPLOAD: [
                MessageHandler(filters.Document.ALL, handle_routes_csv_upload)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
        per_user=True,
        # per_message=False
    )
