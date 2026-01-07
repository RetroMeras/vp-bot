from services.bus_stop import BusStopService
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from handlers.conversations.buses_utils.base_handler import BaseHandler
from handlers.conversations.buses_utils.constants import BusConfig
from handlers.conversations.buses_utils.enums import BusesConversationSteps
from handlers.conversations.buses_utils.messages import BusMessages
from utils.csv_handler import CSVHandler


async def prompt_csv_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt user to upload CSV"""
    await BaseHandler.safe_edit_or_reply(
        update,
        text=BusMessages.csv_upload_instructions(),
        parse_mode='Markdown'
    )
    return BusesConversationSteps.CSV_UPLOAD

async def handle_csv_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process uploaded CSV file"""
    if not update.message:
        return ConversationHandler.END
    if not update.message.document:
        await update.message.reply_text("Пожалуйста, отправьте CSV файл.")
        return BusesConversationSteps.CSV_UPLOAD

    document = update.message.document

    # Validate CSV file
    if not (document.file_name and document.file_name.lower().endswith('.csv')):
        await update.message.reply_text("Пожалуйста, отправьте файл в формате CSV (.csv расширение).")
        return BusesConversationSteps.CSV_UPLOAD

    processing_msg = await update.message.reply_text("⏳ Обрабатываю CSV файл...")

    bus_stop_service = context.bot_data["bus_stop_service"]
    reader = (await CSVHandler.from_file(await document.get_file())).reader()

    count = 0
    for row in reader:
        count += bus_stop_service.add(
            stop_code=row["stop_code"],
            name=row["name"],
            latitude=float(row.get("latitude")) if row.get("latitude") else None,
            longitude=float(row.get("longitude")) if row.get("longitude") else None,
            is_active=row["is_active"] == "true"
        )

    await processing_msg.edit_text(f"✅ Успешно добавлено {count} остановок")
    return ConversationHandler.END

async def handle_csv_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Export stops to CSV"""
    if not update.callback_query:
        return ConversationHandler.END

    await update.callback_query.answer()
    processing_msg = await update.callback_query.edit_message_text("⏳ Подготавливаем CSV файл...")

    bus_stop_service: BusStopService = context.bot_data["bus_stop_service"]
    stops = bus_stop_service.get_all()

    if not stops:
        await update.callback_query.edit_message_text("Нет ни одной остановки.")
        return ConversationHandler.END

    # Generate CSV
    csv_handler = (CSVHandler
        .new(BusConfig.BUS_STOP_COLUMNS)
        .write_rows(map(lambda stop: {
            'id': stop.id,
            'stop_code': stop.stop_code,
            'name': stop.name,
            'latitude': stop.latitude if stop.latitude else '',
            'longitude': stop.longitude if stop.longitude else '',
            'is_active': stop.is_active
        }, stops))).collect()

    # Send file
    message = await BaseHandler.get_effective_message(update)
    if not message:
        await update.callback_query.edit_message_text("Не удалось отправить файл.")
        return ConversationHandler.END

    # type: ignore
    await processing_msg.edit_text("Файл готов! Отправляю...")
    await message.reply_document(
        document=csv_handler.to_file(),
        filename='bus_stops.csv',
        caption='CSV со всеми остановками'
    )

    return ConversationHandler.END