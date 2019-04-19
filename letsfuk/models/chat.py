import uuid
import inject
from datetime import datetime

from letsfuk.db.models import (
    User, Subscriber, Station, PrivateChat,
    StationChat
)
from letsfuk.models.user import User as UserModel


class InvalidMessagePayload(Exception):
    pass


class InvalidLimitOffset(Exception):
    pass


class ReceiverNotFound(Exception):
    pass


class Chat(object):
    @classmethod
    def verify_add_message_receiver(cls, user_id):
        _ = UserModel.get(user_id)

    @classmethod
    def verify_text(cls, text):
        if text is None:
            raise InvalidMessagePayload("Invalid text")
        if len(text) > 600:
            raise InvalidMessagePayload("Text too long, 600 chars is enough")

    @classmethod
    def verify_add_message_payload(cls, payload):
        text = payload.get("text")
        user_id = payload.get("user_id")
        cls.verify_text(text)
        cls.verify_add_message_receiver(user_id)

    @classmethod
    def convert_param(cls, formatted_value):
        value = int(formatted_value[0])
        return value

    @classmethod
    def verify_param(cls, value):
        if value is not None:
            if not isinstance(value, list):
                raise InvalidLimitOffset("Invalid parameter")
            try:
                _ = int(value[0])
            except ValueError as _:
                raise InvalidLimitOffset("Invalid parameter")

    @classmethod
    def verify_params(cls, params):
        offset = params.get("offset")
        limit = params.get("limit")
        cls.verify_param(offset)
        cls.verify_param(limit)

    @classmethod
    def verify_get_messages_payload(cls, receiver_id, params):
        cls.verify_params(params)
        cls.verify_get_messages_receiver(receiver_id)

    @classmethod
    def verify_get_messages_receiver(cls, receiver_id):
        db = inject.instance('db')
        user = UserModel.get(receiver_id)
        station = Station.query_by_station_id(db, receiver_id)
        if user is None and station is None:
            raise ReceiverNotFound(
                "There is not receiver_id: {}".format(receiver_id)
            )

    @classmethod
    def add(cls, payload, sender):
        db = inject.instance('db')
        user_id = payload.get("user_id")
        text = payload.get("text")
        station = Subscriber.get_station_for_user(db, sender.user_id)
        message_id = str(uuid.uuid4())
        sent_at = datetime.utcnow()
        if user_id is not None:
            message = PrivateChat.add(
                db, message_id, user_id, sender.user_id, text, sent_at
            )
            return message
        message = StationChat.add(
            db, message_id, station.station_id, sender.user_id, text, sent_at
        )
        return message

    @classmethod
    def get(cls, receiver_id, sender_id, params):
        # In this format query params are packed
        offset_formatted = params.get("offset", [b'0'])
        limit_formatted = params.get("limit", [b'20'])
        offset = cls.convert_param(offset_formatted)
        limit = cls.convert_param(limit_formatted)
        db = inject.instance('db')
        station = Station.query_by_station_id(db, receiver_id)
        if station is not None:
            messages = StationChat.get(
                db, station.station_id, offset, limit
            )
            station_chat = ChatResponse(station.station_id, messages)
            return station_chat
        messages = PrivateChat.get(
            db, receiver_id, sender_id, offset, limit
        )
        private_chat = ChatResponse(receiver_id, messages)
        return private_chat

    @classmethod
    def get_multiple(cls, sender, params):
        offset_formatted = params.get("offset", [b'0'])
        limit_formatted = params.get("limit", [b'10'])
        offset = cls.convert_param(offset_formatted)
        limit = cls.convert_param(limit_formatted)
        db = inject.instance('db')
        station = Subscriber.get_station_for_user(db, sender.user_id)
        station_chat = cls.get(
            station.station_id, sender.user_id, {}
        )
        chat_user_ids = PrivateChat.get_user_ids_for_user_id(
            db, sender.user_id, offset, limit
        )
        private_chats = []
        for receiver_id in chat_user_ids:
            messages = PrivateChat.get(
                db, receiver_id, sender.user_id, 0, 20
            )
            private_chat = ChatResponse(receiver_id, messages)
            private_chats.append(private_chat)
        return station_chat, private_chats


class ChatResponse(object):
    def __init__(self, receiver_id, messages):
        self.receiver_id = receiver_id
        self.messages = messages

    def to_dict(self):
        return {
            "receiver_id": self.receiver_id,
            "messages": [message.to_dict() for message in self.messages]
        }
# TODO: Subscribe first time per login