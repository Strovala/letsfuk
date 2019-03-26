from letsfuk.decorators import (
    endpoint_wrapper, check_session, resolve_body,
    map_exception)
from letsfuk.errors import BadRequest
from letsfuk.handlers import BaseHandler
from letsfuk.models.station import Station, InvalidLongitude, InvalidLatitude


class StationsHandler(BaseHandler):
    @endpoint_wrapper()
    @check_session()
    @map_exception(out_of=(InvalidLatitude, InvalidLongitude), make=BadRequest)
    @resolve_body()
    def post(self):
        Station.validate_location(self.request.body)
        station = Station.add(self.request.body)
        return station.to_dict(), 200


class SubscribeHandler(BaseHandler):
    def post(self):
        pass
