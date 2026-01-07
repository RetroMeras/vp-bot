from services import Services
from loguru import logger
from utils.base_handler import BaseHandler
from constants import CSVColumns
from utils.csv_handler import CSVHandler
from handlers.conversations.buses.messages import BusMessages
from handlers.conversations.buses.enums import ScheduleMenuAnswers
from handlers.conversations.buses.enums import BusesConversationSteps
from handlers.conversations.buses.keyboards import BusKeyboards
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


async def list_all_schedules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.callback_query:
        return ConversationHandler.END

    query = update.callback_query
    await query.answer()

    services: Services = context.bot_data["services"]
    schedules = services.bus_schedule.get_all()

    await query.edit_message_text(
        "Список всех расписаний:\n" +
        ("\n".join(map(lambda s: f"Марш. {s.route_number} → Остан. {s.stop_code} | {s.departure_time} | Дни: {s.days_of_week}", schedules[:50]))),
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def schedule_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show schedules menu"""
    await BaseHandler.safe_edit_or_reply(
        update,
        text="Меню расписаний",
        reply_markup=BusKeyboards.schedule_menu(),
        parse_mode="Markdown"
    )
    return BusesConversationSteps.SCHEDULES


async def schedule_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    """Handle schedules menu options"""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()

    if query.data == ScheduleMenuAnswers.CSV_UPLOAD:
        return await prompt_schedule_csv_upload(update, context)

    elif query.data == ScheduleMenuAnswers.CSV_EXPORT:
        return await handle_schedule_csv_export(update, context)

    elif query.data == ScheduleMenuAnswers.VIEW_ALL:
        return await list_all_schedules(update, context)

    elif query.data == ScheduleMenuAnswers.BACK:
        await query.edit_message_text(
            "Меню автобусов",
            reply_markup=BusKeyboards.main_menu(),
            parse_mode="Markdown"
        )
        return BusesConversationSteps.BUSES_MENU


async def prompt_schedule_csv_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt user to upload schedules CSV"""
    await BaseHandler.safe_edit_or_reply(
        update,
        text=BusMessages.bus_schedule_upload_instructions(),
        parse_mode='Markdown'
    )
    return BusesConversationSteps.SCHEDULE_CSV_UPLOAD


async def handle_schedule_csv_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Export bus schedules to CSV"""
    if not update.callback_query:
        return ConversationHandler.END

    await update.callback_query.answer()
    processing_msg = await update.callback_query.edit_message_text("⏳ Подготавливаем CSV файл с расписаниями...")

    services: Services = context.bot_data["services"]

    schedules = services.bus_schedule.get_all()

    if not schedules:
        await update.callback_query.edit_message_text("Нет ни одного расписания.")
        return ConversationHandler.END

    # Generate CSV
    csv = (CSVHandler
        .new(CSVColumns.BUS_SCHEDULE)
        .write_rows(map(lambda s: {
            'route_number': s.route_number,
            'stop_code': s.stop_code,
            'departure_time': s.departure_time.strftime('%H:%M:%S'),
            'days_of_week': s.days_of_week,
            'schedule_type': s.schedule_type,
            'notes': s.notes
        }, schedules))
    ).collect()

    # Send file
    message = await BaseHandler.get_effective_message(update)
    if not message:
        await update.callback_query.edit_message_text("Не удалось отправить файл.")
        return ConversationHandler.END
    #type: ignore
    await processing_msg.edit_text("Файл готов! Отправляю...")
    await message.reply_document(
        document=csv.to_file(),
        filename='bus_schedules.csv',
        caption='CSV со всеми расписаниями'
    )

    return ConversationHandler.END


async def handle_schedule_csv_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process uploaded schedules CSV file"""
    if not update.message:
        return ConversationHandler.END
    if not update.message.document:
        await update.message.reply_text("Пожалуйста, отправьте CSV файл.")
        return BusesConversationSteps.SCHEDULE_CSV_UPLOAD

    document = update.message.document

    # Validate CSV file
    if not (document.file_name and document.file_name.lower().endswith('.csv')):
        await update.message.reply_text("Пожалуйста, отправьте файл в формате CSV (.csv расширение).")
        return BusesConversationSteps.SCHEDULE_CSV_UPLOAD

    processing_msg = await update.message.reply_text("⏳ Обрабатываю CSV файл с расписаниями...")

    services: Services = context.bot_data["services"]
    reader = (await CSVHandler.from_file(await document.get_file())).reader()

    count = 0
    for row in reader:
        success, reason = services.bus_schedule.add(
            route_number=int(row["route_number"]),
            stop_code=row["stop_code"],
            departure_time=row["departure_time"],
            days_of_week=int(row["days_of_week"]),
            schedule_type=row.get("schedule_type", "REGULAR"),
            notes=row.get("notes", "")
        )
        if not success:
            logger.warning(reason)
        count += success

    await processing_msg.edit_text(
        f"✅ Успешно добавлено/обновлено {count} расписаний"
    )

    return ConversationHandler.END