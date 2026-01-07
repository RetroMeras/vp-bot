from services import Services
from loguru import logger
from utils.base_handler import BaseHandler
from constants import CSVColumns
from utils.csv_handler import CSVHandler
from handlers.conversations.buses.messages import BusMessages
from handlers.conversations.buses.enums import RouteStopMenuAnswers
from handlers.conversations.buses.enums import BusesConversationSteps
from handlers.conversations.buses.keyboards import BusKeyboards
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


async def list_all_route_stops(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.callback_query:
        return ConversationHandler.END

    query = update.callback_query
    await query.answer()

    services: Services = context.bot_data["services"]
    route_stops = services.bus_route_stop.get_all()

    await query.edit_message_text(
        "Список всех связей маршрут-остановка:\n" +
        ("\n".join(map(lambda rs: f"Route {rs.route_id} → Stop {rs.stop_id} | Dir: {rs.direction} | Seq: {rs.sequence_number}", route_stops))),
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def route_stop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show route stops menu"""
    await BaseHandler.safe_edit_or_reply(
        update,
        text="Меню связей маршрутов и остановок",
        reply_markup=BusKeyboards.route_stop_menu(),
        parse_mode="Markdown"
    )
    return BusesConversationSteps.ROUTE_STOPS


async def route_stop_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    """Handle route stops menu options"""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()

    if query.data == RouteStopMenuAnswers.CSV_UPLOAD:
        return await prompt_route_stop_csv_upload(update, context)

    elif query.data == RouteStopMenuAnswers.CSV_EXPORT:
        return await handle_route_stop_csv_export(update, context)

    elif query.data == RouteStopMenuAnswers.VIEW_ALL:
        return await list_all_route_stops(update, context)

    elif query.data == RouteStopMenuAnswers.BACK:
        logger.info("GO back from route stops")
        return BusesConversationSteps.BUSES_MENU


async def prompt_route_stop_csv_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt user to upload route stops CSV"""
    await BaseHandler.safe_edit_or_reply(
        update,
        text=BusMessages.bus_route_stop_upload_instructions(),
        parse_mode='Markdown'
    )
    return BusesConversationSteps.ROUTE_STOP_CSV_UPLOAD


async def handle_route_stop_csv_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Export bus route stops to CSV"""
    if not update.callback_query:
        return ConversationHandler.END

    await update.callback_query.answer()
    processing_msg = await update.callback_query.edit_message_text("⏳ Подготавливаем CSV файл с связями маршрутов и остановок...")

    services: Services = context.bot_data["services"]

    route_stops = services.bus_route_stop.get_all()

    if not route_stops:
        await update.callback_query.edit_message_text("Нет ни одной связи маршрут-остановка.")
        return ConversationHandler.END

    # Generate CSV
    csv = (CSVHandler
        .new(CSVColumns.BUS_ROUTE_STOP)
        .write_rows(map(lambda rs: {
            'route_id': rs.route_id,
            'stop_id': rs.stop_id,
            'direction': rs.direction,
            'sequence_number': rs.sequence_number
        }, route_stops))
    ).collect()

    # Send file
    message = await BaseHandler.get_effective_message(update)
    if not message:
        await update.callback_query.edit_message_text("Не удалось отправить файл.")
        return ConversationHandler.END
    # type: ignore
    await processing_msg.edit_text("Файл готов! Отправляю...")
    await message.reply_document(
        document=csv.to_file(),
        filename='bus_route_stops.csv',
        caption='CSV со всеми связями маршрутов и остановок'
    )

    return ConversationHandler.END


async def handle_route_stop_csv_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process uploaded route stops CSV file"""
    if not update.message:
        return ConversationHandler.END
    if not update.message.document:
        await update.message.reply_text("Пожалуйста, отправьте CSV файл.")
        return BusesConversationSteps.ROUTE_STOP_CSV_UPLOAD

    document = update.message.document

    # Validate CSV file
    if not (document.file_name and document.file_name.lower().endswith('.csv')):
        await update.message.reply_text("Пожалуйста, отправьте файл в формате CSV (.csv расширение).")
        return BusesConversationSteps.ROUTE_STOP_CSV_UPLOAD

    processing_msg = await update.message.reply_text("⏳ Обрабатываю CSV файл с связями маршрутов и остановок...")

    services: Services = context.bot_data["services"]
    reader = (await CSVHandler.from_file(await document.get_file())).reader()

    count = 0
    for row in reader:
        success, _reason = services.bus_route_stop.add(
            route_number=int(row["route_number"]),
            stop_code=row["stop_code"],
            direction=row.get("direction", "BOTH"),
            sequence_number=int(row["sequence_number"])
        )
        count += success

    await processing_msg.edit_text(
        f"✅ Успешно добавлено/обновлено {count} связей маршрут-остановка"
    )

    return ConversationHandler.END