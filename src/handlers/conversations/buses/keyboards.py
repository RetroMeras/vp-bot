from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from handlers.conversations.buses.enums import (
    BusesMenuAnswers,
    RoutesMenuAnswers,
    RouteStopMenuAnswers,
    ScheduleMenuAnswers,
    StopsMenuAnswers,
)


class BusKeyboards:
    @staticmethod
    def main_menu():
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Остановки", callback_data=BusesMenuAnswers.STOPS),
                InlineKeyboardButton("Автобусы", callback_data=BusesMenuAnswers.BUSES),
                InlineKeyboardButton("Маршрут-Остановка", callback_data=BusesMenuAnswers.ROUTE_STOP)
            ],
            [
                InlineKeyboardButton("Расписание", callback_data=BusesMenuAnswers.SCHEDULE),
                InlineKeyboardButton("Маршруты", callback_data=BusesMenuAnswers.ROUTES)
            ]
        ])

    @staticmethod
    def stops_menu():
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Ближайшая", callback_data=StopsMenuAnswers.CLOSEST),
                InlineKeyboardButton("Просмотр", callback_data=StopsMenuAnswers.VIEW_ALL),
            ],
            [
                InlineKeyboardButton("Загрузить", callback_data=StopsMenuAnswers.CSV_UPLOAD),
                InlineKeyboardButton("Выгрузить", callback_data=StopsMenuAnswers.CSV_EXPORT)
            ],
            [
                InlineKeyboardButton("Назад", callback_data=StopsMenuAnswers.BACK)
            ]
        ])

    @staticmethod
    def routes_menu():
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Просмотр", callback_data=RoutesMenuAnswers.VIEW_ALL)
            ],
            [
                InlineKeyboardButton("Загрузить", callback_data=RoutesMenuAnswers.CSV_UPLOAD),
                InlineKeyboardButton("Выгрузить", callback_data=RoutesMenuAnswers.CSV_EXPORT)
            ],
            [
                InlineKeyboardButton("Назад", callback_data=RoutesMenuAnswers.BACK)
            ]
        ])

    @staticmethod
    def location_request():
        return ReplyKeyboardMarkup(
            [[KeyboardButton("Указать на карте", request_location=True)]],
            resize_keyboard=True, one_time_keyboard=True
        )

    @staticmethod
    def route_stop_menu() -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("Список всех связей", callback_data=RouteStopMenuAnswers.VIEW_ALL)],
            [
                InlineKeyboardButton("Загрузить", callback_data=RouteStopMenuAnswers.CSV_UPLOAD),
                InlineKeyboardButton("Выгрузить", callback_data=RouteStopMenuAnswers.CSV_EXPORT),
            ],
            [InlineKeyboardButton("Назад", callback_data=RouteStopMenuAnswers.BACK)]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def schedule_menu() -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("Список расписаний", callback_data=ScheduleMenuAnswers.VIEW_ALL)],
            [
                InlineKeyboardButton("Загрузить", callback_data=ScheduleMenuAnswers.CSV_UPLOAD),
                InlineKeyboardButton("Выгрузить", callback_data=ScheduleMenuAnswers.CSV_EXPORT),
            ],
            [InlineKeyboardButton("Назад", callback_data=ScheduleMenuAnswers.BACK)]
        ]
        return InlineKeyboardMarkup(keyboard)