import uuid

import datetime
import inject
from datetime import datetime

from letsfuk.db.models import Message as DbMessage, User, Station, Subscriber


class InvalidRegistrationPayload(Exception):
    pass


class UserAlreadyExists(Exception):
    pass


class UserNotFound(Exception):
    pass


class Message(object):
    @classmethod
    def resolve_receiver(cls, db, receiver_id):
        user = User.query_by_user_id(db, receiver_id)
        user_id = None
        if user is not None:
            user_id = user.user_id
        station = Station.query_by_station_id(db, receiver_id)
        station_id = None
        if station is not None:
            station_id = station.station_id
        return station_id, user_id

    @classmethod
    def add(cls, payload, sender):
        db = inject.instance('db')
        user_id = payload.get("user_id")
        sent_at_string = payload.get("sent_at")
        sent_at = datetime.strptime(sent_at_string, '%b %d %Y %H:%M')
        text = payload.get("text")
        station = Subscriber.get_station_for_user(db, sender.user_id)
        station_id = None
        if user_id is None:
            station_id = station.station_id
        message_id = str(uuid.uuid4())
        message = DbMessage.add(
            db, message_id, station_id, user_id,
            sender.user_id, text, sent_at
        )
        return message
