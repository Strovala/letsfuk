import re
import uuid

import bcrypt
import inject

from letsfuk.db.models import User as DbUser


class InvalidRegistrationPayload(Exception):
    pass


class UserAlreadyExists(Exception):
    pass


class UserNotFound(Exception):
    pass


class User(object):
    @classmethod
    def bcrypt_password(cls, password):
        encoded_password = password.encode()
        hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
        decoded_hashed_password = hashed_password.decode()
        return decoded_hashed_password

    @classmethod
    def validate_username(cls, username):
        username_regex = '^\w+$'
        matching = re.match(username_regex, username)
        if not matching or not (3 <= len(username) <= 16):
            raise InvalidRegistrationPayload("Invalid username")

    @classmethod
    def validate_email(cls, email):
        email_regex = (
            '^([a-zA-Z0-9_\-\.]+)'
            '@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$'
        )
        matching = re.match(email_regex, email)
        if not matching:
            raise InvalidRegistrationPayload("Invalid email")

    @classmethod
    def validate_password(cls, password):
        password_regex = '^.*$'
        matching = re.match(password_regex, password)
        if not matching:
            raise InvalidRegistrationPayload("Invalid password")

    @classmethod
    def validate_registration_payload(cls, payload):
        username = payload.get("username", "")
        email = payload.get("email", "")
        password = payload.get("password", "")
        cls.validate_username(username)
        cls.validate_email(email)
        cls.validate_password(password)

    @classmethod
    def add(cls, payload):
        db = inject.instance('db')
        username = payload.get("username")
        email = payload.get("email")
        password = payload.get("password")
        # Check if user with given username already exists
        existing_user = DbUser.query_by_username(db, username)
        if existing_user is not None:
            raise UserAlreadyExists("User with given username already exists")
        else:
            existing_user = DbUser.query_by_email(db, email)
            if existing_user is not None:
                raise UserAlreadyExists(
                    "User with given email already exists"
                )
        bcrypted_password = cls.bcrypt_password(password)
        user_id = str(uuid.uuid4())
        user = DbUser.add(db, user_id, username, email, bcrypted_password)
        return user

    @classmethod
    def get(cls, user_id):
        db = inject.instance('db')
        user = DbUser.query_by_user_id(db, user_id)
        if user is None:
            raise UserNotFound(
                "There is no user with user_id '{}'".format(user_id)
            )
        return user
