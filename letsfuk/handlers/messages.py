from letsfuk.decorators import (
    endpoint_wrapper, check_session, resolve_body,
    map_exception, resolve_user)
from letsfuk.errors import BadRequest, NotFound
from letsfuk.handlers import BaseHandler
from letsfuk.models.message import Message, InvalidMessagePayload
from letsfuk.models.user import UserNotFound


class MessageHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=InvalidMessagePayload, make=BadRequest)
    @map_exception(out_of=UserNotFound, make=NotFound)
    @check_session()
    @resolve_user()
    @resolve_body()
    def post(self):
        Message.verify_payload(self.request.body)
        message = Message.add(
            self.request.body, self.request.user
        )
        return message.to_dict(), 200
