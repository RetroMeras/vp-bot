from services.bus_stop import BusStopService
from enum import Enum
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update
from telegram.ext import ContextTypes

user_data_store = {}

class MainMenuAnswers(str, Enum):
    BUSES = "buses"
    NEWS = "news"
    ABOUT = "about"
    SETTINGS = "settings"

class ConversationStep(ConversationHandler):
    START = -1
    MAINMENU = 0
    BUSES = 1
    STOPS = 5
    # NEWS = 2
    # ABOUT = 3
    # SETTINGS = 4
    ADD_STOP = 6
    ADD_STOP_NAME = 7
    ADD_STOP_LOCATION = 8
    GET_CLOSEST = 9

async def start_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message:
        return ConversationStep.END

    keyboard = [
        [
            InlineKeyboardButton("Автобусы", callback_data=MainMenuAnswers.BUSES),
            InlineKeyboardButton("Новости", callback_data=MainMenuAnswers.NEWS),
        ],
        [
            InlineKeyboardButton("О нас", callback_data=MainMenuAnswers.ABOUT),
            InlineKeyboardButton("Настройки", callback_data=MainMenuAnswers.SETTINGS),
        ]
    ]

    await update.message.reply_text(
        "Основное меню\n"
        "Выберите опцию:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return ConversationStep.MAINMENU

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    query = update.callback_query
    if not query:
        return ConversationStep.START
    await query.answer()

    if query.data == MainMenuAnswers.BUSES:
        return await buses_menu(update, context)
    elif query.data == MainMenuAnswers.NEWS:
        await query.edit_message_text(
            text="Новости в разработке",
            reply_markup=None
        )
        return ConversationStep.START
    elif query.data == MainMenuAnswers.ABOUT:
        await query.edit_message_text(
            text="О нас в разработке",
            reply_markup=None
        )
        return ConversationStep.START
    elif query.data == MainMenuAnswers.SETTINGS:
        await query.edit_message_text(
            text="Настройки в разработке",
            reply_markup=None
        )
        return ConversationStep.START


class BusesMenuAnswers(str, Enum):
    STOPS = "bus stops"
    BUSES = "buses"
    SCHEDULE = "schedule"
    ROUTES = "routes"


async def buses_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    keyboard = [
        [
            InlineKeyboardButton("Остановки", callback_data=BusesMenuAnswers.STOPS),
            InlineKeyboardButton("Автобусы", callback_data=BusesMenuAnswers.BUSES),
        ],
        [
            InlineKeyboardButton("Расписание", callback_data=BusesMenuAnswers.SCHEDULE),
            InlineKeyboardButton("Маршруты", callback_data=BusesMenuAnswers.ROUTES),
        ]
    ]

    if query:
        # Coming from main menu
        await query.edit_message_text(
            text="Меню автобусов",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif update.message:
        await update.message.reply_text(
            text="Меню автобусов",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        return ConversationStep.START

    return ConversationStep.BUSES

async def buses_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    query = update.callback_query
    if not query:
        return ConversationStep.START
    await query.answer()

    if query.data == BusesMenuAnswers.STOPS:
        return await stops_menu(update, context)
    elif query.data == BusesMenuAnswers.BUSES:
        await query.edit_message_text(
            text="Автобусы в разработке",
            reply_markup=None
        )
        return ConversationHandler.END
    elif query.data == BusesMenuAnswers.SCHEDULE:
        await query.edit_message_text(
            text="Расписание в разработке",
            reply_markup=None
        )
        return ConversationHandler.END
    elif query.data == BusesMenuAnswers.ROUTES:
        await query.edit_message_text(
            text="Маршруты в разработке",
            reply_markup=None
        )
        return ConversationHandler.END


class StopsMenuAnswers(str, Enum):
    CLOSEST = "closest"
    CODE = "code"
    MAP = "map"
    ADD = "add"

async def stops_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    query = update.callback_query

    keyboard = [
        [
            InlineKeyboardButton("Ближайшая", callback_data=StopsMenuAnswers.CLOSEST),
            InlineKeyboardButton("На карте", callback_data=StopsMenuAnswers.MAP),
            InlineKeyboardButton("По коду", callback_data=StopsMenuAnswers.CODE),
        ],
        [
            InlineKeyboardButton("Добавить", callback_data=StopsMenuAnswers.ADD),
        ]
    ]

    if query:
        # Coming from buses menu
        await query.edit_message_text(
            text="Меню остановок",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif update.message:
        await update.message.reply_text(
            text="Меню остановок",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        return ConversationStep.START

    return ConversationStep.STOPS


async def stops_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    query = update.callback_query
    if not query:
        return ConversationStep.START
    await query.answer()

    if query.data == StopsMenuAnswers.CLOSEST:
        await query.edit_message_text("Отправьте свой место нахождение (картой или координаты)")
        return ConversationStep.GET_CLOSEST

    elif query.data == StopsMenuAnswers.MAP:
        await query.edit_message_text(
            text="По карте в разработке",
            reply_markup=None
        )
        return ConversationStep.START
    elif query.data == StopsMenuAnswers.CODE:
        await query.edit_message_text(
            text="По коду в разработке",
            reply_markup=None
        )
        return ConversationStep.START
    elif query.data == StopsMenuAnswers.ADD:
        await query.edit_message_text(
            text="➕ **Добавить новую остановку**\n"
                 "Пожалуйста отправьте *код остановки* (пример: BS001):",
            parse_mode='Markdown'
        )
        return ConversationStep.ADD_STOP

async def add_stop_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message or not update.effective_user:
        return ConversationStep.START
    stop_code = (update.message.text or "").strip()

    if not stop_code or not len(stop_code) == 5:
        await update.message.reply_text(
            "❌ Неверный код остановки. Повторите попытку:"
        )
        return ConversationStep.ADD_STOP

    user_id = update.effective_user.id

    user_data_store[user_id] = {
        'stop_code': stop_code
    }

    await update.message.reply_text(
        f"✅ Код остановки: *{stop_code}*\n\n"
        "Теперь название остановки (пример: 'Колос'):",
        parse_mode='Markdown'
    )

    return ConversationStep.ADD_STOP_NAME

async def add_stop_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message or not update.effective_user:
        return ConversationStep.START
    stop_name = (update.message.text or "").strip()

    if not stop_name or not (3 < len(stop_name) < 25):
        await update.message.reply_text(
            "❌ Неверное название. Пожалуйста введите верное название (3-25 символов):"
        )
        return ConversationStep.ADD_STOP_NAME

    user_id = update.effective_user.id

    user_data_store[user_id]['name'] = stop_name

    keyboard = [[KeyboardButton("Указать на карте", request_location=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


    await update.message.reply_text(
        f"✅ Название остановки: *{stop_name}*\n\n"
        "Сейчас, укажите положение остановки.\n"
        "Используйте кнопку ниже или отправьте координаты вручную (latitude,longitude):",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

    return ConversationStep.ADD_STOP_LOCATION


async def add_stop_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message or not update.effective_user:
        return ConversationStep.START

    user_id = update.effective_user.id
    if update.message.location:
        location = update.message.location

        latitude = location.latitude
        longitude = location.longitude

    elif update.message.text:
        coords = update.message.text.strip().split(",")
        if len(coords) != 2:
            await update.message.reply_text(
                "Неверный формат координат",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationStep.ADD_STOP_LOCATION

        latitude = float(coords[0].strip())
        longitude = float(coords[1].strip())
    else:
        await update.message.reply_text(
            "Не найдены координаты.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationStep.ADD_STOP_LOCATION

    user_data_store[user_id]['latitude'] = latitude
    user_data_store[user_id]['longitude'] = longitude

    bus_stop_service: BusStopService = context.bot_data["bus_stop_service"]
    bus_stop_service.add(**user_data_store[user_id])

    await update.message.reply_text(
            f"🎉 *Остановка успешно добавлена!*\n\n"
            f"*Код остановки:* {user_data_store[user_id]["stop_code"]}\n"
            f"*Название:* {user_data_store[user_id]["name"]}\n"
            f"*Координаты:* {user_data_store[user_id]["latitude"]:.6f}, {user_data_store[user_id]["longitude"]:.6f}\n"
            f"[Просмотр на Google Maps](https://maps.google.com/?q={latitude},{longitude})\n\n",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='Markdown',
            disable_web_page_preview=True
        )

    return ConversationStep.BUSES

async def closest_stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message or not update.effective_user:
        return ConversationStep.START

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
            return ConversationStep.GET_CLOSEST

        latitude = float(coords[0].strip())
        longitude = float(coords[1].strip())
    else:
        await update.message.reply_text(
            "Не найдены координаты.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationStep.GET_CLOSEST

    bus_stop_service: BusStopService = context.bot_data["bus_stop_service"]
    closest = bus_stop_service.get_closet(latitude, longitude)
    await update.message.reply_text(
        f"Ближайшая остановка: *{closest.name}*\n"
        f"*Код остановки:* {closest.stop_code}\n"
        "Открыть в [Google Maps](https://maps.google.com/?q={closest.latitude},{closest.longitude})",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    await update.message.reply_location(
        latitude=closest.latitude,
        longitude=closest.longitude,
    )
    return ConversationStep.START

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel and end the conversation."""
    if not update.message or not update.effective_user:
        return ConversationStep.START

    user_id = update.effective_user.id
    if user_id in user_data_store:
        del user_data_store[user_id]

    await update.message.reply_text(
        "❌ Отмена.",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationStep.START