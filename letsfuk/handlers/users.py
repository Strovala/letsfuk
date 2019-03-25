from sqlalchemy.exc import IntegrityError

from letsfuk.decorators import error_handler, resolve_body, map_exception
from letsfuk.errors import BadRequest, Conflict, InternalError
from letsfuk.handlers import BaseHandler
from letsfuk.models import User, InvalidRegistrationPayload, UserAlreadyExists


class UsersHandler(BaseHandler):
    @error_handler()
    @map_exception(out_of=InvalidRegistrationPayload, make=BadRequest)
    @map_exception(out_of=UserAlreadyExists, make=Conflict)
    @map_exception(out_of=IntegrityError, make=InternalError)
    @resolve_body()
    def post(self):
        User.validate_registration_payload(self.request.body)
        user = User.add(self.request.body)
        self.send_response(user.to_dict(), 201)
