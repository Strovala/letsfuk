import logging
import uuid
import inject
from datetime import datetime

from letsfuk import Config
from letsfuk.db.models import (
    User, Subscriber, Station, PrivateChat,
    StationChat, Unread
)
from letsfuk.models.push_notifications import PushNotifications
from letsfuk.models.station import StationNotFound
from letsfuk.models.user import UserNotFound

logger = logging.getLogger(__name__)


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
        if text is not None:
            if type(text) != str:
                raise InvalidPayload("Text must be string!")
            if text == "":
                raise InvalidPayload("Text must not be empty!")
            if len(text) > 600:
                raise InvalidPayload("Text too long, 600 chars is enough!")

    @classmethod
    def verify_image_key(cls, image_key):
        if image_key is not None:
            if type(image_key) != str:
                raise InvalidPayload("Image key must be string!")
            if image_key == "":
                raise InvalidPayload("Image key must not be empty!")

    @classmethod
    def verify_add_message_payload(cls, payload):
        text = payload.get("text")
        user_id = payload.get("user_id")
        image_key = payload.get("image_key")
        cls.verify_image_key(image_key)
        cls.verify_text(text)
        cls.verify_user(user_id)
        if text is None and image_key is None:
            raise InvalidPayload("You must provide either text or image_key!")

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
        value = int(formatted_value)
        return value

    @classmethod
    def verify_param(cls, value):
        try:
            if value is not None:
                _ = int(value)
        except ValueError as _:
            raise InvalidLimitOffset("Invalid parameter")

    @classmethod
    def verify_params(cls, params):
        offset = params.get("offset")
        limit = params.get("limit")
        cls.verify_param(offset)
        cls.verify_param(limit)

    @classmethod
    def get_params(cls, params, default_limit):
        offset_formatted = params.get("offset", 0)
        limit_formatted = params.get("limit", default_limit)
        offset = cls.convert_param(offset_formatted)
        limit = cls.convert_param(limit_formatted)
        return offset, limit

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
    def add_private_message(
            cls, message_id, user_id, sender, text, image_key, sent_at
    ):
        db = inject.instance('db')
        message = PrivateChat.add(
            db, message_id, user_id, sender.user_id, text, image_key, sent_at
        )
        unread = Unread.add(db, user_id, sender_id=sender.user_id)
        message_response = MessageResponse(message)
        data = {
            "is_station": False,
            "unread": unread.count
        }
        data.update(message_response.to_dict())
        from letsfuk import MessageWebSocketHandler
        MessageWebSocketHandler.send_message(
            user_id, event='message',
            data=data
        )
        PushNotifications.send_to_user(user_id, data)
        return MessageResponse(message)

    @classmethod
    def add_station_message(
            cls, message_id, station, sender, text, image_key, sent_at
    ):
        db = inject.instance('db')
        message = StationChat.add(
            db, message_id, station.station_id, sender.user_id,
            text, image_key, sent_at
        )
        station_users = Subscriber.get_users_for_station(
            db, station.station_id
        )
        from letsfuk import MessageWebSocketHandler
        for station_user in station_users:
            if station_user.user_id != sender.user_id:
                unread = Unread.add(
                    db, station_user.user_id, station_id=station.station_id
                )
                message_response = MessageResponse(message)
                data = {
                    "is_station": True,
                    "unread": unread.count
                }
                data.update(message_response.to_dict())
                MessageWebSocketHandler.send_message(
                    station_user.user_id, event='message',
                    data=data
                )
        return MessageResponse(message)

    @classmethod
    def add(cls, payload, sender):
        db = inject.instance('db')
        user_id = payload.get("user_id")
        image_key = payload.get("image_key")
        text = payload.get("text")
        message_id = str(uuid.uuid4())
        sent_at = datetime.utcnow()
        if user_id is not None:
            return cls.add_private_message(
                message_id, user_id, sender, text, image_key, sent_at
            )
        station = Subscriber.get_station_for_user(db, sender.user_id)
        return cls.add_station_message(
            message_id, station, sender, text, image_key, sent_at
        )

    @classmethod
    def get_total(cls, receiver_id, sender_id):
        db = inject.instance('db')
        station = Station.query_by_station_id(db, receiver_id)
        if station is not None:
            total = StationChat.get_total(
                db, station.station_id
            )
            return total
        total = PrivateChat.get_total(
            db, receiver_id, sender_id
        )
        return total

    @classmethod
    def get_total_chats(cls, user):
        db = inject.instance('db')
        total = PrivateChat.get_total_chats(db, user.user_id)
        # Plus one more for station chat
        return total + 1

    @classmethod
    def get(cls, receiver_id, sender_id, params):
        # In this format query params are packed
        config = inject.instance(Config)
        default_chat_limit = config.get('default_chat_limit', 20)
        offset, limit = cls.get_params(params, default_chat_limit)
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
        config = inject.instance(Config)
        default_limit = config.get('default_chat_list_limit', 20)
        offset, limit = cls.get_params(params, default_limit)
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
            default_chat_limit = config.get('default_chat_limit', 20)
            messages = PrivateChat.get(
                db, receiver_id, sender.user_id, 0, default_chat_limit
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


class MessageResponse(object):
    def __init__(self, message):
        self.message = message

        db = inject.instance('db')
        self.sender = dict()
        user = User.query_by_user_id(db, message.sender_id)
        if user is not None:
            self.sender = user.to_dict()

    def to_dict(self):
        result = self.message.to_dict()
        result.pop('sender_id')
        result.update(sender=self.sender)
        return result


class ChatResponse(object):
    def __init__(self, receiver_id, messages, unread=None):
        self.unread = unread

        db = inject.instance('db')
        self.receiver = dict()
        user = User.query_by_user_id(db, receiver_id)
        if user is not None:
            self.receiver = user.to_dict()
            self.receiver.update(id=user.user_id)
            self.receiver.update(is_station=False)
        station = Station.query_by_station_id(db, receiver_id)
        if station is not None:
            self.receiver.update(
                id=station.station_id,
                username="Station",
                is_station=True
            )

        # TODO: Now that avatar_key is changable maybe update cache or clear it
        # when avatar is changed

        # self.messages = [
        #     Memcache.get_or_set_dict(
        #         'messages-{}'.format(message.message_id),
        #         self._to_message_response_dict, message
        #     )
        #     for message in reversed(messages)
        # ]

        # for now, no caching
        self.messages = [
            MessageResponse(message).to_dict()
            for message in reversed(messages)
        ]

    @staticmethod
    def _to_message_response_dict(message):
        message_reponse = MessageResponse(message)
        return message_reponse.to_dict()

    def to_dict(self):
        return {
            "receiver": self.receiver,
            "unread": self.unread,
            "messages": self.messages
        }
