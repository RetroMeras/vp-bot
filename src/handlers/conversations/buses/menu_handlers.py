from handlers.conversations.buses.schedule_handlers import schedule_menu
from handlers.conversations.buses.route_stop_handlers import route_stop_menu
from utils.base_handler import BaseHandler
from handlers.conversations.buses.route_handlers import routes_menu
from handlers.conversations.buses.stops_handlers import stops_menu
from handlers.conversations.buses.enums import BusesMenuAnswers
from handlers.conversations.buses.enums import BusesConversationSteps
from handlers.conversations.buses.keyboards import BusKeyboards
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

async def buses_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message:
        return ConversationHandler.END

    await BaseHandler.safe_edit_or_reply(
        update,
        text="Меню автобусов",
        reply_markup=BusKeyboards.main_menu(),
        parse_mode="Markdown"
    )
    return BusesConversationSteps.BUSES_MENU

async def buses_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    query = update.callback_query
    if not query:
        return ConversationHandler.END
    await query.answer()

    if query.data == BusesMenuAnswers.STOPS:
        return await stops_menu(update, context)
    elif query.data == BusesMenuAnswers.BUSES:
        await query.edit_message_text(text="Автобусы в разработке")
        return ConversationHandler.END
    elif query.data == BusesMenuAnswers.ROUTE_STOP:
        return await route_stop_menu(update, context)
    elif query.data == BusesMenuAnswers.SCHEDULE:
        return await schedule_menu(update, context)
    elif query.data == BusesMenuAnswers.ROUTES:
        return await routes_menu(update, context)