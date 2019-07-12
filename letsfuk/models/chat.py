import uuid
import inject
from datetime import datetime

from letsfuk.db.models import (
    User, Subscriber, Station, PrivateChat,
    StationChat, Unread
)
from letsfuk.models.station import StationNotFound
from letsfuk.models.user import UserNotFound


class InvalidPayload(Exception):
    pass


class InvalidLimitOffset(Exception):
    pass


class ReceiverNotFound(Exception):
    pass


class InvalidCount(Exception):
    pass


class Chat(object):
    @classmethod
    def verify_user(cls, user_id):
        db = inject.instance('db')
        if user_id is not None:
            user = User.query_by_user_id(db, user_id)
            if user is None:
                raise UserNotFound(
                    "There is no user with user id: {}".format(user_id)
                )

    @classmethod
    def verify_station(cls, station_id):
        db = inject.instance('db')
        if station_id is not None:
            station = Station.query_by_station_id(db, station_id)
            if station is None:
                raise StationNotFound(
                    "There is no station with id: {}".format(station_id)
                )

    @classmethod
    def verify_text(cls, text):
        if text is None:
            raise InvalidPayload("Invalid text")
        if len(text) > 600:
            raise InvalidPayload("Text too long, 600 chars is enough")

    @classmethod
    def verify_add_message_payload(cls, payload):
        text = payload.get("text")
        user_id = payload.get("user_id")
        cls.verify_text(text)
        cls.verify_user(user_id)

    @classmethod
    def verify_int(cls, value):
        if not isinstance(value, int):
            raise InvalidCount("Count must be integer")

    @classmethod
    def verify_reset_unread(cls, payload):
        station_id = payload.get('station_id')
        sender_id = payload.get('sender_id')
        count = payload.get('count')
        if station_id is None and sender_id is None:
            raise InvalidPayload(
                "Both station_id and sender_id can't be empty"
            )
        cls.verify_station(station_id)
        cls.verify_user(sender_id)
        cls.verify_int(count)

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
        user = User.query_by_user_id(db, receiver_id)
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
        from letsfuk import MessageWebSocketHandler
        if user_id is not None:
            message = PrivateChat.add(
                db, message_id, user_id, sender.user_id, text, sent_at
            )
            unread = Unread.add(db, user_id, sender_id=sender.user_id)
            MessageWebSocketHandler.send_message(
                user_id, event='message',
                data={
                    "is_station": False,
                    "message": message.to_dict(),
                    "sender_id": sender.user_id,
                    "unread": unread.count
                }
            )
            return message
        message = StationChat.add(
            db, message_id, station.station_id, sender.user_id, text, sent_at
        )
        station_users = Subscriber.get_users_for_station(
            db, station.station_id
        )
        for station_user in station_users:
            if station_user.user_id == sender.user_id:
                continue
            unread = Unread.add(
                db, station_user.user_id, station_id=station.station_id
            )
            MessageWebSocketHandler.send_message(
                station_user.user_id, event='message',
                data={
                    "is_station": True,
                    "message": message.to_dict(),
                    "sender_id": station.station_id,
                    "unread": unread.count
                }
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
            unread_count = cls.get_unread_in_station_for_user(
                sender_id, station.station_id
            )
            station_chat = ChatResponse(
                station.station_id, messages, unread_count
            )
            return station_chat
        messages = PrivateChat.get(
            db, receiver_id, sender_id, offset, limit
        )
        unread_count = cls.get_unread_in_private_for_user(
            sender_id, receiver_id
        )
        private_chat = ChatResponse(receiver_id, messages, unread_count)
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
            unread_count = cls.get_unread_in_private_for_user(
                sender.user_id, receiver_id
            )
            private_chat = ChatResponse(receiver_id, messages, unread_count)
            private_chats.append(private_chat)
        return station_chat, private_chats

    @classmethod
    def get_unread_in_station_for_user(cls, user_id, station_id):
        db = inject.instance('db')
        unread = Unread.get(db, user_id, station_id=station_id)
        unread_count = 0
        if unread is not None:
            unread_count = unread.count
        return unread_count

    @classmethod
    def get_unread_in_private_for_user(cls, user_id, sender_id):
        db = inject.instance('db')
        unread = Unread.get(db, user_id, sender_id=sender_id)
        unread_count = 0
        if unread is not None:
            unread_count = unread.count
        return unread_count

    @classmethod
    def reset_unread(cls, payload, user):
        station_id = payload.get('station_id')
        sender_id = payload.get('sender_id')
        count = payload.get('count')
        db = inject.instance('db')
        unread = Unread.reset(
            db, user.user_id, station_id=station_id,
            sender_id=sender_id, count=count
        )
        return unread


class ChatResponse(object):
    def __init__(self, receiver_id, messages, unread=None):
        self.receiver_id = receiver_id
        self.messages = messages
        self.unread = unread

    def to_dict(self):
        return {
            "receiver_id": self.receiver_id,
            "unread": self.unread,
            "messages": [message.to_dict() for message in self.messages]
        }
# TODO: Write test for unreads
