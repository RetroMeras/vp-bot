from enum import Enum
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional

class UserRole(str, Enum):
    USER = "user"
    MODERATOR = "editor"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class User(SQLModel, table=True):
    telegram_id: int = Field(unique=True, index=True, primary_key=True)
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_interaction: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    role: UserRole = Field(default=UserRole.USER)

class UserUpdate(SQLModel):
    username: Optional[str] = None
    last_interaction: Optional[datetime] = None


class BusStop(SQLModel, table=True):
    id: int = Field(primary_key=True)
    stop_code: str = Field(unique=True, nullable=False, index=True)
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: bool = True

class BusRoute(SQLModel, table=True):
    id: int = Field(primary_key=True)
    route_number: int = Field(unique=True, nullable=False, index=True)
    name: str
    first_stop_code: str = Field(foreign_key="busstop.stop_code")
    last_stop_code: str = Field(foreign_key="busstop.stop_code")
    is_active: bool = True
    color_hex: str = Field(default='#007BFF')


class BusRouteStop(SQLModel, table=True):
    id: int = Field(primary_key=True)
    route_number: int = Field(foreign_key="busroute.route_number")
    stop_code: str = Field(foreign_key="busstop.stop_code")
    direction: str = "BOTH"
    sequence_number: int

class BusSchedule(SQLModel, table=True):
    id: int = Field(primary_key=True)
    route_number: int = Field(foreign_key="busroute.route_number")
    stop_code: int = Field(foreign_key="busstop.stop_code")
    departure_time: str # HH:MM 24 hours
    days_of_week: int # TODO change to one byte
    schedule_type: str = Field(default="REGULAR")
    notes: str