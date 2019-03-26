import uuid

import inject
from letsfuk.db.models import Station as DbStation


class InvalidLatitude(Exception):
    pass


class InvalidLongitude(Exception):
    pass


class Station(object):
    @classmethod
    def validate_latitude(cls, lat):
        in_range = -90 <= lat <= 90
        if not in_range:
            raise InvalidLatitude("Latitude need to be between -90 and 90")

    @classmethod
    def validate_longitude(cls, lon):
        in_range = -180 <= lon <= 180
        if not in_range:
            raise InvalidLatitude("Latitude need to be between -180 and 180")

    @classmethod
    def validate_location(cls, payload):
        lat = payload.get('lat')
        lon = payload.get('lon')
        cls.validate_latitude(lat)
        cls.validate_longitude(lon)

    @classmethod
    def add(cls, payload):
        lat = payload.get('lat')
        lon = payload.get('lon')
        db = inject.instance('db')
        station_id = str(uuid.uuid4())
        DbStation.add(db, station_id, lat, lon)
