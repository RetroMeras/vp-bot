from enum import Enum

class BusesConversationSteps(int, Enum):
    BUSES_MENU = 0
    BUSES = 0
    STOPS = 2
    ROUTES = 3
    SCHEDULE = 4
    GET_CLOSEST = 5
    CSV_UPLOAD = 6
    ROUTES_CSV_UPLOAD = 7
    ROUTE_STOPS = 8
    ROUTE_STOP_CSV_UPLOAD = 9
    SCHEDULES = 10
    SCHEDULE_CSV_UPLOAD = 11

class BusesMenuAnswers(str, Enum):
    STOPS = "bus_stops"
    ROUTE_STOP = "bus_route_stop"
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


class RouteStopMenuAnswers(str, Enum):
    VIEW_ALL = "route_stops_view_all"
    CSV_UPLOAD = "route_stops_csv_upload"
    CSV_EXPORT = "route_stops_csv_export"
    BACK = "route_stops_back"

class ScheduleMenuAnswers(str, Enum):
    VIEW_ALL = "schedules_view_all"
    CSV_UPLOAD = "schedules_csv_upload"
    CSV_EXPORT = "schedules_csv_export"
    BACK = "schedules_back"