from letsfuk.decorators import (
    endpoint_wrapper, check_session, resolve_body,
    map_exception, resolve_user
)
from letsfuk.errors import BadRequest, NotFound
from letsfuk.handlers import BaseHandler
from letsfuk.models.chat import (
    Chat, InvalidPayload,
    InvalidLimitOffset,
    ReceiverNotFound,
    InvalidCount
)
from letsfuk.models.station import StationNotFound
from letsfuk.models.user import UserNotFound


class MessagesHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=InvalidPayload, make=BadRequest)
    @map_exception(out_of=UserNotFound, make=NotFound)
    @check_session()
    @resolve_user()
    @resolve_body()
    def post(self):
        Chat.verify_add_message_payload(self.request.body)
        message = Chat.add(
            self.request.body, self.request.user
        )
        return message.to_dict(), 200

    @endpoint_wrapper()
    @map_exception(out_of=InvalidPayload, make=BadRequest)
    @map_exception(out_of=UserNotFound, make=NotFound)
    @check_session()
    @resolve_user()
    def get(self):
        Chat.verify_params(self.request.params)
        station_chat, private_chats = Chat.get_multiple(
            self.request.user, self.request.params
        )
        return {
            "station_chat": station_chat.to_dict(),
            "private_chats": [chat.to_dict() for chat in private_chats]
        }, 200


class ChatMessagesHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(out_of=InvalidLimitOffset, make=BadRequest)
    @map_exception(out_of=ReceiverNotFound, make=NotFound)
    @check_session()
    @resolve_user()
    def get(self, receiver_id):
        Chat.verify_get_messages_payload(
            receiver_id, self.request.params
        )
        chat = Chat.get(
            receiver_id, self.request.user.user_id, self.request.params
        )
        total = Chat.get_total(receiver_id, self.request.user.user_id)
        self.set_header('x-total', total)
        return chat.to_dict(), 200


class UnreadMessagesHandler(BaseHandler):
    @endpoint_wrapper()
    @map_exception(
        out_of=(InvalidCount, UserNotFound, StationNotFound, InvalidPayload),
        make=BadRequest
    )
    @check_session()
    @resolve_user()
    @resolve_body()
    def put(self):
        Chat.verify_reset_unread(self.request.body)
        unread = Chat.reset_unread(self.request.body, self.request.user)
        return unread.to_dict(), 200
