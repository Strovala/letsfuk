import uuid

import inject

from letsfuk.db.models import Message as DbMessage


class InvalidRegistrationPayload(Exception):
    pass


class UserAlreadyExists(Exception):
    pass


class UserNotFound(Exception):
    pass


class Message(object):
    @classmethod
    def add(cls, payload, receiver_id, sender):
        db = inject.instance('db')
        username = payload.get("message")
        email = payload.get("email")
        password = payload.get("password")
        message_id = str(uuid.uuid4())
        DbMessage.add(db, message_id, receiver_id, sender.user_id)
