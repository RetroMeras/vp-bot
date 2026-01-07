from services.bus_schedule import BusScheduleService
from services.bus_route_stop import BusRouteStopService
from dataclasses import dataclass
from .user import UserService
from .admin import AdminService
from .bus_stop import BusStopService
from .bus_route import BusRouteService

@dataclass
class Services:
    user: UserService
    admin: AdminService
    bus_stop: BusStopService
    bus_route: BusRouteService
    bus_route_stop: BusRouteStopService
    bus_schedule: BusScheduleService

def create_services() -> Services:
    return Services(
        user=UserService(),
        admin=AdminService(),
        bus_stop=BusStopService(),
        bus_route=BusRouteService(),
        bus_route_stop=BusRouteStopService(),
        bus_schedule=BusScheduleService()
    )