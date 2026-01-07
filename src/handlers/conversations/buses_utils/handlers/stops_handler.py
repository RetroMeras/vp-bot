from handlers.conversations.buses_utils.handlers.add_stops_handlers import list_all_stops
from handlers.conversations.buses_utils.handlers.csv_handlers import handle_csv_export, prompt_csv_upload
from handlers.conversations.buses_utils.handlers.add_stops_handlers import prompt_add_stop
from handlers.conversations.buses_utils.keyboards import BusKeyboards
from handlers.conversations.buses_utils.enums import StopsMenuAnswers, BusesConversationSteps
from handlers.conversations.buses_utils.base_handler import BaseHandler
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

async def stops_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await BaseHandler.safe_edit_or_reply(
        update,
        text="Меню остановок",
        reply_markup=BusKeyboards.stops_menu(),
        parse_mode="Markdown"
    )
    return BusesConversationSteps.STOPS

async def stops_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    query = update.callback_query
    if not query:
        return ConversationHandler.END
    await query.answer()

    if query.data == StopsMenuAnswers.CLOSEST:
        await query.edit_message_text("Отправьте свое местоположение (картой или координаты)")
        return BusesConversationSteps.GET_CLOSEST
    elif query.data == StopsMenuAnswers.VIEW_ALL:
        return await list_all_stops(update, context)
    elif query.data == StopsMenuAnswers.ADD:
        return await prompt_add_stop(update, context)
    elif query.data == StopsMenuAnswers.CSV_UPLOAD:
        return await prompt_csv_upload(update, context)
    elif query.data == StopsMenuAnswers.CSV_EXPORT:
        return await handle_csv_export(update, context)