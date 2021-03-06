from letsfuk.decorators import (
    endpoint_wrapper, check_session, resolve_body,
    map_exception, resolve_user
)
from letsfuk.errors import BadRequest, NotFound
from letsfuk.handlers import BaseHandler
from letsfuk.models.station import (
    Station, InvalidLongitude, InvalidLatitude,
    Subscriber,
    StationNotFound)
from letsfuk.models.user import UserNotFound, User


class StationsHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=(InvalidLatitude, InvalidLongitude), make=BadRequest)
    @check_session()
    @resolve_body()
    def post(self):
        Station.validate_location(self.request.body)
        station = Station.add(self.request.body)
        return station.to_dict(), 200


class StationHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=StationNotFound, make=NotFound)
    @check_session()
    def get(self, station_id):
        station = Station.get(station_id)
        members = Station.get_members(station)
        return {
           "station": station.to_dict(),
           "members": [member.to_dict() for member in members]
        }, 200


class SubscribeHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=(InvalidLatitude, InvalidLongitude), make=BadRequest)
    @check_session()
    @resolve_user()
    @resolve_body()
    def post(self):
        Station.validate_location(self.request.body)
        subscriber = Subscriber.add(self.request.body, self.request.user)
        return subscriber.to_dict(), 200

    @endpoint_wrapper()
    @map_exception(out_of=UserNotFound, make=NotFound)
    @check_session()
    @resolve_user()
    def get(self, user_id):
        user = User.get(user_id)
        station = Station.get_for_user(user)
        return station.to_dict(), 200
