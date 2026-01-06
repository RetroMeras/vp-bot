from handlers.conversations.buses_utils.enums import BusesConversationSteps
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

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
            return BusesConversationSteps.ADD_STOP_LOCATION

        latitude = float(coords[0].strip())
        longitude = float(coords[1].strip())
    else:
        await update.message.reply_text("Не найдены координаты.", reply_markup=ReplyKeyboardRemove())
        return BusesConversationSteps.GET_CLOSEST

    # Find closest stop
    bus_stop_service = context.bot_data["bus_stop_service"]
    closest = bus_stop_service.get_closest(latitude, longitude)

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