from typing import Optional
from sqlmodel import select
from services.base import BaseService

from database.models import BusRouteStop, BusStop, BusRoute

class BusRouteStopService(BaseService):
    def __init__(self):
        super().__init__()

    def add(self, route_number: int, stop_code: str, direction: str, sequence_number: int) -> tuple[bool, str]:
        """Add a new bus route stop"""
        if self.session.exec(select(BusRouteStop).where(
                BusRouteStop.route_number == route_number and
                BusRouteStop.stop_code == stop_code and
                BusRouteStop.sequence_number == sequence_number)
            ).first():
            return False, "Эта остановка уже была добавлена с таким номером уже существует"

        if not self.session.exec(select(BusStop).where(BusStop.stop_code == stop_code)).first():
            return False, f"Не существует остановки с кодом `{stop_code}`"

        if not self.session.exec(select(BusRoute).where(BusRoute.route_number == route_number)).first():
            return False, f"Не существует маршрута с номером `{route_number}`"

        route_stop = BusRouteStop(
            route_number = route_number,
            stop_code = stop_code,
            direction = direction,
            sequence_number = sequence_number
        )
        self.session.add(route_stop)
        self.session.commit()
        return True, ""

    def get_all(self) -> list[BusRouteStop]:
        """Get all routes"""
        return list(self.session.exec(select(BusRouteStop)).all())

    def get_by_id(self, route_id: int) -> Optional[BusRouteStop]:
        """Get route by ID"""
        return self.session.exec(select(BusRouteStop).where(BusRouteStop.id == route_id)).first()