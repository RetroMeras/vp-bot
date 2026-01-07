from constants import BusConfig
from services.bus_stop import BusStopService
from handlers.conversations.buses_utils.data_manager import UserDataManager
from handlers.conversations.buses_utils.keyboards import BusKeyboards
from handlers.conversations.buses_utils.enums import BusesConversationSteps
from handlers.conversations.buses_utils.base_handler import BaseHandler
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

user_data_manager = UserDataManager()

async def list_all_stops(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.callback_query:
        return ConversationHandler.END

    query = update.callback_query
    await query.answer()

    bus_stop_service: BusStopService = context.bot_data["bus_stop_service"]
    stops = bus_stop_service.get_all()

    await query.edit_message_text(
        "Список всех остановок:\n" +
        ("\n".join(map(lambda stop: f"{stop.stop_code} | *{stop.name}*", stops))),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def prompt_add_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Initial prompt for adding a stop"""
    await BaseHandler.safe_edit_or_reply(
        update,
        text="➕ **Добавить новую остановку**\nПожалуйста отправьте *код остановки* (пример: BS001):",
        parse_mode='Markdown'
    )
    return BusesConversationSteps.ADD_STOP

async def add_stop_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle stop code input"""
    if not update.message:
        return ConversationHandler.END

    stop_code = (update.message.text or "").strip()
    if not stop_code or not len(stop_code) == BusConfig.STOP_CODE_LENGTH:
        await update.message.reply_text(
            "❌ Неверный код остановки. Повторите попытку:",
            reply_markup=ReplyKeyboardRemove()
        )
        return BusesConversationSteps.ADD_STOP

    user_id = BaseHandler.get_user_id(update)
    if not user_id:
        return ConversationHandler.END
    user_data_manager.set_stop_code(user_id, stop_code)

    await update.message.reply_text(
        f"✅ Код остановки: *{stop_code}*\n\nТеперь название остановки (пример: 'Колос'):",
        parse_mode='Markdown'
    )
    return BusesConversationSteps.ADD_STOP_NAME

async def add_stop_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle stop name input"""
    if not update.message:
        return ConversationHandler.END

    stop_name = (update.message.text or "").strip()
    if not stop_name or not (BusConfig.MIN_STOP_NAME_LENGTH < len(stop_name) < BusConfig.MAX_STOP_NAME_LENGTH):
        await update.message.reply_text(
            "❌ Неверное название. Пожалуйста введите верное название (3-25 символов):",
            reply_markup=ReplyKeyboardRemove()
        )
        return BusesConversationSteps.ADD_STOP_NAME

    user_id = BaseHandler.get_user_id(update)
    if not user_id:
        return ConversationHandler.END
    user_data_manager.set_name(user_id, stop_name)

    await update.message.reply_text(
        f"✅ Название остановки: *{stop_name}*\n\n"
        "Сейчас, укажите положение остановки.\n"
        "Используйте кнопку ниже или отправьте координаты вручную (latitude,longitude):",
        reply_markup=BusKeyboards.location_request(),
        parse_mode='Markdown'
    )
    return BusesConversationSteps.ADD_STOP_LOCATION

async def add_stop_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle location input and save the stop"""
    if not update.message:
        return ConversationHandler.END

    user_id = BaseHandler.get_user_id(update)
    if not user_id:
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
            return BusesConversationSteps.ADD_STOP_LOCATION

        latitude = float(coords[0].strip())
        longitude = float(coords[1].strip())
    else:
        await update.message.reply_text("Не найдены координаты.", reply_markup=ReplyKeyboardRemove())
        return BusesConversationSteps.ADD_STOP_LOCATION

    # Save location and create stop
    user_data = user_data_manager.get_stop_data(user_id)
    user_data.update({'latitude': latitude, 'longitude': longitude})

    # Save to service
    bus_stop_service = context.bot_data["bus_stop_service"]
    bus_stop_service.add(**user_data)

    # Clear user data
    user_data_manager.clear_user_data(user_id)

    # Send confirmation
    await update.message.reply_text(
        f"🎉 *Остановка успешно добавлена!*\n\n"
        f"*Код остановки:* {user_data['stop_code']}\n"
        f"*Название:* {user_data['name']}\n"
        f"*Координаты:* {latitude:.6f}, {longitude:.6f}\n"
        f"[Просмотр на Google Maps](https://maps.google.com/?q={latitude},{longitude})",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown',
        disable_web_page_preview=True
    )
    return ConversationHandler.END