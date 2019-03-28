import datetime
import uuid

import bcrypt
import inject

from letsfuk import Config
from letsfuk.db.models import Session
from letsfuk.db.models import User


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
            user = User.query_by_email(db, email)
        elif username is not None:
            user = User.query_by_username(db, username)
        if user is None:
            raise WrongCredentials("Wrong username/email or password")
        encoded_password = password.encode()
        encoded_hashed_password = user.password.encode()
        matching = bcrypt.checkpw(encoded_password, encoded_hashed_password)
        if not matching:
            raise WrongCredentials("Wrong username/email or password")
        existing_session = Session.query_by_user_id(db, user.user_id)
        if existing_session is not None:
            return {
                "user": user.to_dict(),
                "session_id": existing_session.session_id
            }
        session_id = str(uuid.uuid4())
        config = inject.instance(Config)
        session_ttl = config.get('session_ttl', 30)
        now = datetime.datetime.now()
        expires_at = now + datetime.timedelta(minutes=session_ttl)
        _ = Session.add(db, session_id, user.user_id, expires_at)
        return user, session_id

    @classmethod
    def logout(cls, session):
        db = inject.instance('db')
        _ = Session.delete(db, session)
