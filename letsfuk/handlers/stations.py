from letsfuk.decorators import (
    endpoint_wrapper,
    check_session
)
from letsfuk.handlers import BaseHandler
from letsfuk.models.station import Station


class StationsSubscribeHandler(BaseHandler):
    @endpoint_wrapper()
    @check_session()
    def post(self):
        Station.validate_location(self.request.body)
        Station.add(self.request.body)
