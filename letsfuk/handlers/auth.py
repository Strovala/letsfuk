from letsfuk.decorators import (
    check_session, error_handler, resolve_body, map_exception
)
from letsfuk.errors import BadRequest
from letsfuk.handlers import BaseHandler
from letsfuk.models import Auth, WrongCredentials


class LoginHandler(BaseHandler):
    @error_handler()
    @map_exception(out_of=WrongCredentials, make=BadRequest)
    @resolve_body()
    def post(self):
        response = Auth.login(self.request.body)
        self.send_response(response, 200)


class LogoutHandler(BaseHandler):
    @error_handler()
    @check_session()
    def post(self):
        Auth.logout(self.request.session)
        self.send_response("You are successfully logged out", 200)
