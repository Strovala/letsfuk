from letsfuk.decorators import (
    endpoint_wrapper, check_session, resolve_body,
    map_exception, resolve_user
)
from letsfuk.errors import BadRequest, NotFound
from letsfuk.handlers import BaseHandler
from letsfuk.models.station import (
    Station, InvalidLongitude, InvalidLatitude,
    Subscriber
)
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
        station = Subscriber.get(user)
        return station.to_dict(), 200
