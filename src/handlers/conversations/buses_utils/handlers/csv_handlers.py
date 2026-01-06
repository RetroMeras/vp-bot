from handlers.conversations.buses_utils.enums import BusesConversationSteps
from handlers.conversations.buses_utils.messages import BusMessages
from handlers.conversations.buses_utils.base_handler import BaseHandler
import csv
import io
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

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

    # Download and process
    file = await document.get_file()
    file_bytes = await file.download_as_bytearray()
    content = file_bytes.decode("utf-8")

    reader = csv.DictReader(io.StringIO(content))
    bus_stop_service = context.bot_data["bus_stop_service"]

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

    bus_stop_service = context.bot_data["bus_stop_service"]
    stops = bus_stop_service.get_all()

    if not stops:
        await update.callback_query.edit_message_text("Нет ни одной остановки.")
        return ConversationHandler.END

    # Generate CSV
    output = io.StringIO()
    fieldnames = ['id', 'stop_code', 'name', 'latitude', 'longitude', 'is_active']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for stop in stops:
        writer.writerow({
            'id': stop.id,
            'stop_code': stop.stop_code,
            'name': stop.name,
            'latitude': stop.latitude if stop.latitude else '',
            'longitude': stop.longitude if stop.longitude else '',
            'is_active': stop.is_active
        })

    # Send file
    message = await BaseHandler.get_effective_message(update)
    if not message:
        await update.callback_query.edit_message_text("Не удалось отправить файл.")
        return ConversationHandler.END

    # type: ignore
    await processing_msg.edit_text("Файл готов! Отправляю...")
    await message.reply_document(
        document=io.BytesIO(output.getvalue().encode("utf-8")),
        filename='bus_stops.csv',
        caption='CSV со всеми остановками'
    )

    return ConversationHandler.END