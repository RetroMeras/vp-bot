from enum import Enum

class BusesConversationSteps(int, Enum):
    BUSES_MENU = 0
    BUSES = 0
    STOPS = 2
    ROUTES = 3
    SCHEDULE = 4
    GET_CLOSEST = 5
    CSV_UPLOAD = 9
    ROUTES_CSV_UPLOAD = 10

class BusesMenuAnswers(str, Enum):
    STOPS = "bus_stops"
    BUSES = "buses"
    SCHEDULE = "schedule"
    ROUTES = "routes"

class RoutesMenuAnswers(str, Enum):
    CSV_UPLOAD = "routes_upload_csv"
    CSV_EXPORT = "routes_export_csv"
    VIEW_ALL = "routes_view_all"
    BACK = "back"

class StopsMenuAnswers(str, Enum):
    CLOSEST = "stops_closest"
    VIEW_ALL = "stops_view_all"
    CSV_UPLOAD = "stops_upload_csv"
    CSV_EXPORT = "stops_export_csv"
    BACK = "back"