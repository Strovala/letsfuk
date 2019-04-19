import uuid

import inject
from letsfuk.db.models import Station as DbStation
from letsfuk.db.models import Subscriber as DbSubscriber


class InvalidLatitude(Exception):
    pass


class InvalidLongitude(Exception):
    pass


class Station(object):
    @classmethod
    def validate_latitude(cls, lat):
        if lat is None:
            raise InvalidLatitude("Latitude need to be between -90 and 90")
        in_range = -90 <= lat <= 90
        if not in_range:
            raise InvalidLatitude("Latitude need to be between -90 and 90")

    @classmethod
    def validate_longitude(cls, lon):
        if lon is None:
            raise InvalidLatitude("Latitude need to be between -180 and 180")
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
        station = DbStation.add(db, station_id, lat, lon)
        return station

    @classmethod
    def get_closest(cls, lat, lon):
        db = inject.instance('db')
        station = DbStation.get_closest(db, lat, lon)
        return station


class Subscriber(object):
    @classmethod
    def add(cls, payload, user):
        lat = payload.get('lat')
        lon = payload.get('lon')
        station = Station.get_closest(lat, lon)
        db = inject.instance('db')
        subscriber = DbSubscriber.add(db, station.station_id, user.user_id)
        return subscriber

    @classmethod
    def get(cls, user):
        db = inject.instance('db')
        station = DbSubscriber.get_station_for_user(db, user.user_id)
        return station
