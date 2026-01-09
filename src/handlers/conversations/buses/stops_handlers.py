from services import Services
from loguru import logger
from constants import CSVColumns
from utils.csv_handler import CSVHandler
from handlers.conversations.buses.messages import BusMessages
from utils.base_handler import BaseHandler
from handlers.conversations.buses.keyboards import BusKeyboards
from handlers.conversations.buses.enums import StopsMenuAnswers, BusesConversationSteps
from telegram import Update, ReplyKeyboardRemove
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
        await query.edit_message_text("Отправьте своё местоположение (картой или координаты)")
        return BusesConversationSteps.GET_CLOSEST

    elif query.data == StopsMenuAnswers.VIEW_ALL:
        return await list_all_stops(update, context)

    elif query.data == StopsMenuAnswers.CSV_UPLOAD:
        return await prompt_csv_upload(update, context)

    elif query.data == StopsMenuAnswers.CSV_EXPORT:
        return await handle_csv_export(update, context)

    elif query.data == StopsMenuAnswers.BACK:
        await query.edit_message_text(
            "Меню автобусов",
            reply_markup=BusKeyboards.main_menu(),
            parse_mode="Markdown"
        )
        return BusesConversationSteps.BUSES_MENU

async def list_all_stops(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.callback_query:
        return ConversationHandler.END

    query = update.callback_query
    await query.answer()

    services: Services = context.bot_data["services"]
    stops = services.bus_stop.get_all()

    await query.edit_message_text(
        "Список всех остановок:\n" +
        ("\n".join(map(lambda stop: f"{stop.stop_code} | *{stop.name}*", stops))),
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def prompt_csv_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt user to upload CSV"""
    await BaseHandler.safe_edit_or_reply(
        update,
        text=BusMessages.bus_stops_upload_instructions(),
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

    services: Services = context.bot_data["services"]
    reader = (await CSVHandler.from_file(await document.get_file())).reader()

    count = 0
    for row in reader:
        success, reason = services.bus_stop.add(
            stop_code=row["stop_code"],
            name=row["name"],
            latitude=float(row.get("latitude")) if row.get("latitude") else None,
            longitude=float(row.get("longitude")) if row.get("longitude") else None,
            is_active=row.get("is_active", "true") == "true"
        )
        if not success:
            logger.warning(reason)
        count += success

    await processing_msg.edit_text(f"✅ Успешно добавлено {count} остановок")
    return ConversationHandler.END

async def handle_csv_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Export stops to CSV"""
    if not update.callback_query:
        return ConversationHandler.END

    await update.callback_query.answer()
    processing_msg = await update.callback_query.edit_message_text("⏳ Подготавливаем CSV файл...")

    services: Services = context.bot_data["services"]
    stops = services.bus_stop.get_all()

    if not stops:
        await update.callback_query.edit_message_text("Нет ни одной остановки.")
        return ConversationHandler.END

    # Generate CSV
    csv_handler = (CSVHandler
        .new(CSVColumns.BUS_STOP)
        .write_rows(map(lambda stop: {
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


    if type(processing_msg) is bool:
        return ConversationHandler.END

    await processing_msg.edit_text("Файл готов! Отправляю...")
    await message.reply_document(
        document=csv_handler.to_file(),
        filename='bus_stops.csv',
        caption='CSV со всеми остановками'
    )

    return ConversationHandler.END


async def closest_stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Find closest bus stop to user's location"""
    if not update.message:
        return ConversationHandler.END

    # Extract coordinates
    if update.message.location:
        latitude = update.message.location.latitude
        longitude = update.message.location.longitude
    elif update.message.text:
        coords = update.message.text.strip().split(",")
        if len(coords) != 2:
            await update.message.reply_text(
                "Неверный формат координат",
                reply_markup=ReplyKeyboardRemove()
            )
            return BusesConversationSteps.GET_CLOSEST

        latitude = float(coords[0].strip())
        longitude = float(coords[1].strip())
    else:
        await update.message.reply_text("Не найдены координаты.", reply_markup=ReplyKeyboardRemove())
        return BusesConversationSteps.GET_CLOSEST

    # Find closest stop
    services: Services = context.bot_data["services"]
    closest = services.bus_stop.get_closest(latitude, longitude)

    # Send results
    await update.message.reply_text(
        f"Ближайшая остановка: *{closest.name}*\n"
        f"*Код остановки:* {closest.stop_code}\n"
        f"Открыть в [Google Maps](https://maps.google.com/?q={closest.latitude},{closest.longitude})",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    await update.message.reply_location(
        latitude=closest.latitude,
        longitude=closest.longitude,
    )
    return ConversationHandler.END