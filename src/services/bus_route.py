"""Service for bus route operations"""
from database.models import BusStop
from services.base import BaseService
from typing import Optional
from sqlmodel import select
from database.models import BusRoute

class BusRouteService(BaseService):
    def __init__(self):
        super().__init__()

    def add(self, route_number: int, name: str, first_stop_code: str, last_stop_code: str, is_active: bool = True, color_hex: str = "#007BFF") -> tuple[bool, str]:
        """Add a new bus route"""
        if self.session.exec(select(BusRoute).where(BusRoute.route_number == route_number)).first():
            return False, "Маршрут с таким номером уже существует"

        if not self.session.exec(select(BusStop).where(BusStop.stop_code == first_stop_code)).first():
            return False, f"Не существует остановки с кодом `{first_stop_code}`"

        if not self.session.exec(select(BusStop).where(BusStop.stop_code == last_stop_code)).first():
            return False, f"Не существует остановки с кодом `{last_stop_code}`"

        route = BusRoute(
            route_number = route_number,
            name = name,
            first_stop_code = first_stop_code,
            last_stop_code = last_stop_code,
            is_active = is_active,
            color_hex = color_hex
        )
        self.session.add(route)
        self.session.commit()
        return True, ""

    def get_all(self) -> list[BusRoute]:
        """Get all routes"""
        return list(self.session.exec(select(BusRoute)).all())

    def get_by_route_number(self, route_number: str) -> Optional[BusRoute]:
        """Get route by route number"""
        return self.session.exec(select(BusRoute).where(BusRoute.route_number == route_number)).first()

    def get_by_id(self, route_id: int) -> Optional[BusRoute]:
        """Get route by ID"""
        return self.session.exec(select(BusRoute).where(BusRoute.id == route_id)).first()