from letsfuk.decorators import (
    check_session, endpoint_wrapper, resolve_body, map_exception
)
from letsfuk.errors import BadRequest
from letsfuk.handlers import BaseHandler
from letsfuk.models.auth import Auth, WrongCredentials


class LoginHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=WrongCredentials, make=BadRequest)
    @resolve_body()
    def post(self):
        user, session_id = Auth.login(self.request.body)
        return {
            "user": user.to_dict(),
            "session_id": session_id
        }, 200


class LogoutHandler(BaseHandler):
    @endpoint_wrapper()
    @check_session()
    def post(self):
        Auth.logout(self.request.session)
        return "You are successfully logged out", 200
