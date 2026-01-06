from handlers.conversations.buses_utils.enums import StopsMenuAnswers, BusesMenuAnswers
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

class BusKeyboards:
    @staticmethod
    def main_menu():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Остановки", callback_data=BusesMenuAnswers.STOPS),
             InlineKeyboardButton("Автобусы", callback_data=BusesMenuAnswers.BUSES)],
            [InlineKeyboardButton("Расписание", callback_data=BusesMenuAnswers.SCHEDULE),
             InlineKeyboardButton("Маршруты", callback_data=BusesMenuAnswers.ROUTES)]
        ])

    @staticmethod
    def stops_menu():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Ближайшая", callback_data=StopsMenuAnswers.CLOSEST)],
            [InlineKeyboardButton("Добавить", callback_data=StopsMenuAnswers.ADD),
             InlineKeyboardButton("Загрузить", callback_data=StopsMenuAnswers.CSV_UPLOAD),
             InlineKeyboardButton("Выгрузить", callback_data=StopsMenuAnswers.CSV_EXPORT)]
        ])

    @staticmethod
    def location_request():
        return ReplyKeyboardMarkup(
            [[KeyboardButton("Указать на карте", request_location=True)]],
            resize_keyboard=True, one_time_keyboard=True
        )