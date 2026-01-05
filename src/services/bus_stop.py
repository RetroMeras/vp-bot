from math import radians, cos, sin, asin, sqrt
from typing import Optional
from sqlmodel import select

from services.base import BaseService
from database.models import BusStop


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r


class BusStopService(BaseService):
    def __init__(self):
        super().__init__()

    def add(self, stop_code: str, name: str, is_active: bool = True, latitude: Optional[float] = None, longitude: Optional[float] = None) -> bool:
        if self.session.exec(select(BusStop).where(BusStop.stop_code == stop_code)).first():
            return False

        stop = BusStop(stop_code=stop_code, name=name, latitude=latitude, longitude=longitude, is_active=is_active)
        self.session.add(stop)
        self.session.commit()
        return True

    def get_id(self, id: int) -> BusStop:
        return self.session.exec(select(BusStop).where(BusStop.id == id)).one()

    def get_stop_code(self, stop_code: int) -> BusStop:
        return self.session.exec(select(BusStop).where(BusStop.stop_code == stop_code)).one()

    # TODO: possibly optimize
    def get_closet(self, latitude: float, longitude: float) -> BusStop:
        stops = self.session.exec(select(BusStop)).all()
        if len(stops) == 0:
            raise ValueError("No bus stops were created.")
        if len(stops) == 1:
            return stops[0]

        closest = stops[0]
        shortest_distance = haversine(longitude, latitude, closest.longitude, closest.latitude)

        for stop in stops[1:]:
            distance = haversine(longitude, latitude, stop.longitude, stop.latitude)
            if distance < shortest_distance:
                closest = stop
                shortest_distance = distance

        return stop
