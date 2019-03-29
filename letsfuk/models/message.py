import uuid

import datetime
import inject
from datetime import datetime

from letsfuk.db.models import Message as DbMessage, User, Subscriber, Station
from letsfuk.models.user import UserNotFound


class InvalidMessagePayload(Exception):
    pass


class InvalidLimitOffset(Exception):
    pass


class ReceiverNotFound(Exception):
    pass


class Message(object):
    @classmethod
    def verify_add_message_receiver(cls, user_id):
        db = inject.instance('db')
        if user_id is not None:
            user = User.query_by_user_id(db, user_id)
            if user is None:
                raise UserNotFound(
                    "There is no user with user id: {}".format(user_id)
                )

    @classmethod
    def verify_text(cls, text):
        if text is None:
            raise InvalidMessagePayload("Invalid text")
        if len(text) > 600:
            raise InvalidMessagePayload("Text too long, 600 chars is enough")

    @classmethod
    def verify_sent_at(cls, sent_at):
        if sent_at is None:
            raise InvalidMessagePayload("Invalid sent_at attribute")
        _ = cls.string_to_datetime(sent_at)

    @classmethod
    def verify_add_message_payload(cls, payload):
        sent_at = payload.get("sent_at")
        text = payload.get("text")
        user_id = payload.get("user_id")
        cls.verify_sent_at(sent_at)
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
    def string_to_datetime(cls, sent_at):
        try:
            sent_at = datetime.strptime(sent_at, '%b %d %Y %H:%M:%S.%f')
        except ValueError as _:
            raise InvalidMessagePayload("Invalid sent_at attribute")
        return sent_at

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
        sent_at_string = payload.get("sent_at")
        text = payload.get("text")
        sent_at = cls.string_to_datetime(sent_at_string)
        station = Subscriber.get_station_for_user(db, sender.user_id)
        station_id = station.station_id if user_id is None else None
        message_id = str(uuid.uuid4())
        message = DbMessage.add(
            db, message_id, station_id, user_id,
            sender.user_id, text, sent_at
        )
        return message

    @classmethod
    def get(cls, receiver_id, sender_id, params):
        # In this format query params are packed
        offset_formatted =  params.get("offset", [b'0'])
        limit_formatted =  params.get("limit", [b'20'])
        offset = cls.convert_param(offset_formatted)
        limit = cls.convert_param(limit_formatted)
        db = inject.instance('db')
        messages = DbMessage.get(db, receiver_id, sender_id, offset, limit)
        return messages
