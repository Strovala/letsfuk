from letsfuk.decorators import (
    endpoint_wrapper,
    check_session
)
from letsfuk.handlers import BaseHandler


class StationsSubscribeHandler(BaseHandler):
    @endpoint_wrapper()
    @check_session()
    def post(self):
        x = 1
