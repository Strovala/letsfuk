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
        response = Auth.login(self.request.body)
        return response, 200


class LogoutHandler(BaseHandler):
    @endpoint_wrapper()
    @check_session()
    def post(self):
        Auth.logout(self.request.session)
        return "You are successfully logged out", 200
