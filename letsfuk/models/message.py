import uuid

import datetime
import inject
from datetime import datetime

from letsfuk.db.models import Message as DbMessage, User, Subscriber
from letsfuk.models.user import UserNotFound


class InvalidMessagePayload(Exception):
    pass


class Message(object):
    @classmethod
    def verify_receiver(cls, user_id):
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
    def verify_payload(cls, payload):
        sent_at = payload.get("sent_at")
        text = payload.get("text")
        user_id = payload.get("user_id")
        cls.verify_sent_at(sent_at)
        cls.verify_text(text)
        cls.verify_receiver(user_id)

    @classmethod
    def string_to_datetime(cls, sent_at):
        try:
            sent_at = datetime.strptime(sent_at, '%b %d %Y %H:%M:%S.%f')
        except ValueError as _:
            raise InvalidMessagePayload("Invalid sent_at attribute")
        return sent_at

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
