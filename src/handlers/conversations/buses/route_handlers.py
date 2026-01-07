from services import Services
from loguru import logger
from utils.base_handler import BaseHandler
from constants import CSVColumns
from utils.csv_handler import CSVHandler
from handlers.conversations.buses.messages import BusMessages
from handlers.conversations.buses.enums import RoutesMenuAnswers
from handlers.conversations.buses.enums import BusesConversationSteps
from handlers.conversations.buses.keyboards import BusKeyboards
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

async def list_all_routes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.callback_query:
        return ConversationHandler.END

    query = update.callback_query
    await query.answer()

    services: Services = context.bot_data["services"]
    routes = services.bus_route.get_all()

    await query.edit_message_text(
        "Список всех маршрутов:\n" +
        ("\n".join(map(lambda route: f"{route.route_number} | *{route.name}*", routes))),
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def routes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show routes menu"""
    await BaseHandler.safe_edit_or_reply(
        update,
        text="Меню маршрутов",
        reply_markup=BusKeyboards.routes_menu(),
        parse_mode="Markdown"
    )
    return BusesConversationSteps.ROUTES

async def routes_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    """Handle routes menu options"""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()

    if query.data == RoutesMenuAnswers.CSV_UPLOAD:
        return await prompt_routes_csv_upload(update, context)

    elif query.data == RoutesMenuAnswers.CSV_EXPORT:
        return await handle_routes_csv_export(update, context)

    elif query.data == RoutesMenuAnswers.VIEW_ALL:
        # Handle viewing routes
        return await list_all_routes(update, context)

    elif query.data == RoutesMenuAnswers.BACK:
        logger.info("GO back from stops")
        return BusesConversationSteps.BUSES_MENU

async def prompt_routes_csv_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt user to upload routes CSV"""
    await BaseHandler.safe_edit_or_reply(
        update,
        text=BusMessages.bus_routes_upload_instructions(),
        parse_mode='Markdown'
    )
    return BusesConversationSteps.ROUTES_CSV_UPLOAD

async def handle_routes_csv_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Export bus routes to CSV"""
    if not update.callback_query:
        return ConversationHandler.END

    await update.callback_query.answer()
    processing_msg = await update.callback_query.edit_message_text("⏳ Подготавливаем CSV файл с маршрутами...")

    services: Services = context.bot_data["services"]

    routes = services.bus_route.get_all()

    if not routes:
        await update.callback_query.edit_message_text("Нет ни одного маршрута.")
        return ConversationHandler.END

    # Generate CSV
    csv = (CSVHandler
        .new(CSVColumns.BUS_ROUTE)
        .write_rows(map(lambda route: {
            'route_number': route.route_number,
            'name': route.name,
            'first_stop_code': route.first_stop_code,
            'last_stop_code': route.last_stop_code,
            'is_active': route.is_active,
            'color_hex': route.color_hex
        }, routes))
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
        filename='bus_routes.csv',
        caption='CSV со всеми маршрутами'
    )

    return ConversationHandler.END

async def handle_routes_csv_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process uploaded routes CSV file"""
        if not update.message:
            return ConversationHandler.END
        if not update.message.document:
            await update.message.reply_text("Пожалуйста, отправьте CSV файл.")
            return BusesConversationSteps.ROUTES_CSV_UPLOAD

        document = update.message.document

        # Validate CSV file
        if not (document.file_name and document.file_name.lower().endswith('.csv')):
            await update.message.reply_text("Пожалуйста, отправьте файл в формате CSV (.csv расширение).")
            return BusesConversationSteps.ROUTES_CSV_UPLOAD

        processing_msg = await update.message.reply_text("⏳ Обрабатываю CSV файл с маршрутами...")

        services: Services = context.bot_data["services"]
        # Download and process
        reader = (await CSVHandler.from_file(await document.get_file())).reader()

        count = 0
        for route in reader:
            success, _reason = services.bus_route.add(
                route_number=int(route["route_number"]),
                name=route["name"],
                first_stop_code=route["first_stop_code"],
                last_stop_code=route["last_stop_code"],
                is_active=route.get("is_active", "true") == "true",
                color_hex=route["color_hex"],
            )
            count += success


        await processing_msg.edit_text(
            f"✅ Успешно добавлено/обновлено {count} маршрутов, "
        )

        return ConversationHandler.END