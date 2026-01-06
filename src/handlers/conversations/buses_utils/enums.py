from enum import Enum

class BusesConversationSteps(int, Enum):
    BUSES = 1
    STOPS = 2
    ROUTES = 3
    SCHEDULE = 4
    GET_CLOSEST = 5
    ADD_STOP = 6
    ADD_STOP_NAME = 7
    ADD_STOP_LOCATION = 8
    CSV_UPLOAD = 9


class BusesMenuAnswers(str, Enum):
    STOPS = "bus_stops"
    BUSES = "buses"
    SCHEDULE = "schedule"
    ROUTES = "routes"


class StopsMenuAnswers(str, Enum):
    CLOSEST = "closest"
    ADD = "add"
    CSV_UPLOAD = "upload_csv"
    CSV_EXPORT = "export_csv"