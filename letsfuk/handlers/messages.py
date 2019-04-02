from letsfuk.decorators import (
    endpoint_wrapper, check_session, resolve_body,
    map_exception, resolve_user
)
from letsfuk.errors import BadRequest, NotFound
from letsfuk.handlers import BaseHandler
from letsfuk.models.chat import (
    Chat, InvalidMessagePayload,
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
        Chat.verify_add_message_payload(self.request.body)
        chat = Chat.add(
            self.request.body, self.request.user
        )
        return chat.to_dict(), 200


class ChatMessagesHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=InvalidLimitOffset, make=BadRequest)
    @map_exception(out_of=ReceiverNotFound, make=NotFound)
    @check_session()
    @resolve_user()
    def get(self, receiver_id):
        Chat.verify_get_messages_payload(
            receiver_id, self.request.arguments
        )
        chat = Chat.get(
            receiver_id, self.request.user.user_id, self.request.arguments
        )
        return {
            "messages": [message.to_dict() for message in chat]
        }, 200
