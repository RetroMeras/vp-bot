"""Service for bus schedule operations"""
from typing import Optional
from sqlmodel import select
from services.base import BaseService
from database.models import BusSchedule, BusRoute, BusStop


class BusScheduleService(BaseService):
    def __init__(self):
        super().__init__()

    def add(
        self,
        route_number: int,
        stop_code: str,
        departure_time: str,
        days_of_week: int,
        schedule_type: str = "REGULAR",
        notes: str = ""
    ) -> tuple[bool, str]:
        """Add a new bus schedule"""
        # Check if route exists
        if not self.session.exec(select(BusRoute).where(BusRoute.route_number == route_number)).first():
            return False, f"Не существует маршрута с ID `{route_number}`"

        # Check if stop exists
        if not self.session.exec(select(BusStop).where(BusStop.stop_code == stop_code)).first():
            return False, f"Не существует остановки с ID `{stop_code}`"

        # Check if schedule already exists
        if self.session.exec(select(BusSchedule)
                .where(BusSchedule.route_number == route_number)
                .where(BusSchedule.stop_code == stop_code)
                .where(BusSchedule.departure_time == departure_time)
                .where(BusSchedule.days_of_week == days_of_week)
            ).first():
            return False, "Расписание с такими параметрами уже существует"

        schedule = BusSchedule(
            route_number=route_number,
            stop_code=stop_code,
            departure_time=departure_time,
            days_of_week=days_of_week,
            schedule_type=schedule_type,
            notes=notes
        )
        self.session.add(schedule)
        self.session.commit()
        return True, ""

    def get_all(self) -> list[BusSchedule]:
        """Get all schedules"""
        return list(self.session.exec(select(BusSchedule)).all())

    def get_by_id(self, schedule_id: int) -> Optional[BusSchedule]:
        """Get schedule by ID"""
        return self.session.exec(select(BusSchedule).where(BusSchedule.id == schedule_id)).first()

    def get_by_route(self, route_number: int) -> list[BusSchedule]:
        """Get all schedules for a specific route"""
        return list(self.session.exec(
            select(BusSchedule)
            .where(BusSchedule.route_number == route_number)
            .order_by(BusSchedule.departure_time)
        ).all())