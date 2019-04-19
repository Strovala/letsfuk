from letsfuk.decorators import (
    check_session, endpoint_wrapper, resolve_body, map_exception
)
from letsfuk.errors import BadRequest
from letsfuk.handlers import BaseHandler
from letsfuk.models.auth import Auth, WrongCredentials
from letsfuk.models.station import (
    InvalidLatitude, InvalidLongitude, Station,
    Subscriber
)


class LoginHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=WrongCredentials, make=BadRequest)
    @map_exception(out_of=(InvalidLatitude, InvalidLongitude), make=BadRequest)
    @resolve_body()
    def post(self):
        Station.validate_location(self.request.body)
        user, session_id = Auth.login(self.request.body)
        subscriber = Subscriber.add(self.request.body, user)
        return {
            "user": user.to_dict(),
            "session_id": session_id,
            'station_id': subscriber.station_id
        }, 200


class LogoutHandler(BaseHandler):
    @endpoint_wrapper()
    @check_session()
    def post(self):
        Auth.logout(self.request.session)
        return "You are successfully logged out", 200
