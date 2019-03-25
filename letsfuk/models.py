import re

import bcrypt
from sqlalchemy.exc import IntegrityError

from letsfuk import db
from letsfuk.database.models import User as DbUser


class InvalidRegistrationPayload(Exception):
    pass


class InvalidUsername(InvalidRegistrationPayload):
    def __init__(self):
        super(InvalidUsername, self).__init__(
            "Usernames can consist of lowercase and capitals\n"
            "Usernames can consist of alphanumeric characters\n"
            "Usernames can consist of underscore and hyphens\n"
            "Usernames cannot be two underscores, two hypens "
            "or two spaces in a row\n"
            "Usernames cannot have a underscore, hypen or "
            "space at the start or end\n"
        )


class UserAlreadyExists(Exception):
    pass


class UserNotFound(Exception):
    pass


class User(object):
    @classmethod
    def validate_username(cls, username):
        username_regex = '^[a-zA-Z0-9]+([_-]?[a-zA-Z0-9])*$'
        matching = re.match(username_regex, username)
        if not matching or not (3 <= len(username) <= 12):
            raise InvalidUsername()

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
        username = payload.get("username")
        email = payload.get("email")
        password = payload.get("password")
        cls.validate_username(username)
        cls.validate_email(email)
        cls.validate_password(password)

    @classmethod
    def add(cls, payload):
        username = payload.get("username")
        email = payload.get("email")
        password = payload.get("password")
        # Check if user with given username already exists
        existing_user = DbUser.query.filter_by(username=username).first()
        if existing_user is not None:
            raise UserAlreadyExists()
        encoded_password = password.encode()
        hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
        decoded_hashed_password = hashed_password.decode()
        user = DbUser(
            username=username, password=decoded_hashed_password, email=email
        )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            db.session.remove()
            raise e
        return user

    @classmethod
    def get(cls, username):
        user = DbUser.query.filter_by(username=username).first()
        if user is None:
            raise UserNotFound()
        return user
