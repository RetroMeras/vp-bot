from handlers.conversations.buses.route_stop_handlers import handle_route_stop_csv_upload
from handlers.conversations.buses.route_stop_handlers import route_stop_menu_handler
from handlers.conversations.buses.schedule_handlers import handle_schedule_csv_upload
from handlers.conversations.buses.schedule_handlers import schedule_menu_handler
from handlers.conversations.buses.enums import ScheduleMenuAnswers
from handlers.conversations.buses.enums import RouteStopMenuAnswers
from handlers.conversations.buses.route_handlers import handle_routes_csv_upload, routes_menu_handler
from handlers.conversations.buses.stops_handlers import handle_csv_upload, closest_stop_handler
from handlers.conversations.buses.enums import RoutesMenuAnswers
from handlers.conversations.buses.stops_handlers import stops_menu_handler
from handlers.conversations.buses.menu_handlers import buses_menu, buses_menu_handler
from handlers.conversations.buses.enums import StopsMenuAnswers, BusesMenuAnswers, BusesConversationSteps
from handlers.cancel_handler import cancel
from telegram.ext import ConversationHandler, BaseHandler, CallbackQueryHandler, CommandHandler, MessageHandler, filters

def get_buses_conversation_handler() -> BaseHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("buses", buses_menu)],
        states={
            BusesConversationSteps.BUSES_MENU: [CallbackQueryHandler(buses_menu_handler, pattern=f"^({'|'.join([option for option in BusesMenuAnswers])})$")],
            BusesConversationSteps.STOPS: [CallbackQueryHandler(stops_menu_handler, pattern=f"^({'|'.join([option for option in StopsMenuAnswers])})$")],
            BusesConversationSteps.GET_CLOSEST: [MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.LOCATION, closest_stop_handler)],
            BusesConversationSteps.CSV_UPLOAD: [MessageHandler(filters.Document.ALL, handle_csv_upload)],
            BusesConversationSteps.ROUTES: [
                CallbackQueryHandler(routes_menu_handler,
                    pattern=f"^({'|'.join([option for option in RoutesMenuAnswers])})$")
            ],
            BusesConversationSteps.ROUTES_CSV_UPLOAD: [
                MessageHandler(filters.Document.ALL, handle_routes_csv_upload)
            ],
            BusesConversationSteps.ROUTE_STOPS: [
                CallbackQueryHandler(route_stop_menu_handler, pattern=f"^({'|'.join([option for option in RouteStopMenuAnswers])})$")
            ],
            BusesConversationSteps.ROUTE_STOP_CSV_UPLOAD: [
                MessageHandler(filters.Document.ALL, handle_route_stop_csv_upload)
            ],
            BusesConversationSteps.SCHEDULES: [
                CallbackQueryHandler(schedule_menu_handler, pattern=f"^({'|'.join([option for option in ScheduleMenuAnswers])})$")
            ],
            BusesConversationSteps.SCHEDULE_CSV_UPLOAD: [
                MessageHandler(filters.Document.ALL, handle_schedule_csv_upload)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
        per_user=True,
    )
