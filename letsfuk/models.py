import datetime
import re
import uuid

import bcrypt
import inject
from sqlalchemy.exc import IntegrityError

from letsfuk.db.models import User as DbUser, Session


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
        username_regex = '^\w+$'
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
        encoded_password = password.encode()
        hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
        decoded_hashed_password = hashed_password.decode()
        user = DbUser(
            username=username, password=decoded_hashed_password, email=email
        )
        db.add(user)
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise e
        return user

    @classmethod
    def get(cls, username):
        db = inject.instance('db')
        user = DbUser.query_by_username(db, username)
        if user is None:
            raise UserNotFound(
                "There is no user with username '{}'".format(username)
            )
        return user


class WrongCredentials(Exception):
    pass


class Auth(object):
    @classmethod
    def login(cls, payload):
        db = inject.instance('db')
        username = payload.get("username")
        password = payload.get("password", "")
        email = payload.get("email")
        user = None
        if email is not None:
            user = DbUser.query_by_email(db, email)
        elif username is not None:
            user = DbUser.query_by_username(db, username)
        if user is None:
            raise WrongCredentials("Wrong username/email or password")
        encoded_password = password.encode()
        encoded_hashed_password = user.password.encode()
        matching = bcrypt.checkpw(encoded_password, encoded_hashed_password)
        if not matching:
            raise WrongCredentials("Wrong username/email or password")
        existing_session = Session.query_by_user_id(db, user.id)
        if existing_session is not None:
            return {
                "user": user.to_dict(),
                "session_id": existing_session.session_id
            }
        session_id = str(uuid.uuid4())
        # TODO: make config file
        session_ttl = 30
        now = datetime.datetime.now()
        expires_at = now + datetime.timedelta(minutes=session_ttl)
        _ = Session.add(db, session_id, user.id, expires_at)
        return {
            "user": user.to_dict(),
            "session_id": session_id
        }

    @classmethod
    def logout(cls, session):
        db = inject.instance('db')
        _ = Session.delete(db, session)
