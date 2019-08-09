from sqlalchemy.exc import IntegrityError
from letsfuk.decorators import (
    endpoint_wrapper, resolve_body,
    map_exception, check_session,
    resolve_user)
from letsfuk.errors import BadRequest, Conflict, InternalError, NotFound
from letsfuk.handlers import BaseHandler
from letsfuk.models.user import (
    User, InvalidPayload,
    UserAlreadyExists, UserNotFound
)


class UsersHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=InvalidPayload, make=BadRequest)
    @map_exception(out_of=UserAlreadyExists, make=Conflict)
    @map_exception(out_of=IntegrityError, make=InternalError)
    @resolve_body()
    def post(self):
        User.validate_registration_payload(self.request.body)
        user = User.add(self.request.body)
        return user.to_dict(), 200


class UserHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=UserNotFound, make=NotFound)
    @check_session()
    def get(self, user_id):
        user = User.get(user_id)
        return user.to_dict(), 200

    @endpoint_wrapper()
    @map_exception(out_of=InvalidPayload, make=BadRequest)
    @check_session()
    @resolve_body()
    def patch(self, user_id):
        User.validate_avatar(self.request.body)
        user = User.update_avatar(user_id, self.request.body)
        return user.to_dict(), 200


class WhoAmIHandler(BaseHandler):
    @endpoint_wrapper()
    @check_session()
    @map_exception(out_of=UserNotFound, make=NotFound)
    def get(self):
        user = User.get_by_session(self.request.session)
        return {
            "user": user.to_dict(),
            "session_id": self.request.session.session_id
         }, 200
