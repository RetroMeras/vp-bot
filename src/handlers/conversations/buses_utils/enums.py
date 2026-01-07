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
    ROUTES_CSV_UPLOAD = 10
    ROUTES_MENU = 11

class RoutesMenuAnswers(str, Enum):
    CSV_UPLOAD = "routes_upload_csv"
    CSV_EXPORT = "routes_export_csv"
    VIEW_ALL = "routes_view_all"
    ADD = "routes_add"

class BusesMenuAnswers(str, Enum):
    STOPS = "bus_stops"
    BUSES = "buses"
    SCHEDULE = "schedule"
    ROUTES = "routes"


class StopsMenuAnswers(str, Enum):
    CLOSEST = "stops_closest"
    VIEW_ALL = "stops_view_all"
    ADD = "stops_add"
    CSV_UPLOAD = "stops_upload_csv"
    CSV_EXPORT = "stops_export_csv"