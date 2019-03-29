from letsfuk.decorators import (
    endpoint_wrapper, check_session, resolve_body,
    map_exception, resolve_user
)
from letsfuk.errors import BadRequest, NotFound
from letsfuk.handlers import BaseHandler
from letsfuk.models.message import (
    Message, InvalidMessagePayload,
    InvalidLimitOffset,
    ReceiverNotFound
)
from letsfuk.models.user import UserNotFound


class MessagesHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=InvalidMessagePayload, make=BadRequest)
    @map_exception(out_of=UserNotFound, make=NotFound)
    @check_session()
    @resolve_user()
    @resolve_body()
    def post(self):
        Message.verify_add_message_payload(self.request.body)
        message = Message.add(
            self.request.body, self.request.user
        )
        return message.to_dict(), 200


class StationMessagesHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=InvalidLimitOffset, make=BadRequest)
    @map_exception(out_of=ReceiverNotFound, make=NotFound)
    @check_session()
    @resolve_user()
    def get(self, receiver_id):
        Message.verify_get_messages_payload(
            receiver_id, self.request.arguments
        )
        messages = Message.get(
            receiver_id, self.request.user.user_id, self.request.arguments
        )
        return {
            "messages": [message.to_dict() for message in messages]
        }, 200
