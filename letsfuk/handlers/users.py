from sqlalchemy.exc import IntegrityError
from letsfuk.decorators import (
    endpoint_wrapper, resolve_body,
    map_exception, check_session
)
from letsfuk.errors import BadRequest, Conflict, InternalError, NotFound
from letsfuk.handlers import BaseHandler
from letsfuk.models.user import (
    User, InvalidRegistrationPayload,
    UserAlreadyExists, UserNotFound
)


class UsersHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=InvalidRegistrationPayload, make=BadRequest)
    @map_exception(out_of=UserAlreadyExists, make=Conflict)
    @map_exception(out_of=IntegrityError, make=InternalError)
    @resolve_body()
    def post(self):
        User.validate_registration_payload(self.request.body)
        user = User.add(self.request.body)
        return user.to_dict(), 201


class UserHandler(BaseHandler):
    @endpoint_wrapper()
    @check_session()
    @map_exception(out_of=UserNotFound, make=NotFound)
    def get(self, username):
        user = User.get(username)
        return user.to_dict(), 200
