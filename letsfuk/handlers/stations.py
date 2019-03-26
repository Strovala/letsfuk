from letsfuk.decorators import (
    endpoint_wrapper, check_session, resolve_body
)
from letsfuk.handlers import BaseHandler
from letsfuk.models.station import Station


class StationsSubscribeHandler(BaseHandler):
    @endpoint_wrapper()
    @check_session()
    @resolve_body()
    def post(self):
        Station.validate_location(self.request.body)
        station = Station.add(self.request.body)
        return station.to_dict(), 200
