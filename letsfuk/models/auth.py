import datetime
import uuid
import logging
import bcrypt
import inject

from letsfuk import Config
from letsfuk.db.models import Session
from letsfuk.db.models import User

logger = logging.getLogger(__name__)


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
        if user is None and username is not None:
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
            return user, existing_session.session_id
        session_id = str(uuid.uuid4())
        config = inject.instance(Config)
        session_ttl = config.get('session_ttl', 946100000)
        now = datetime.datetime.utcnow()
        expires_at = now + datetime.timedelta(seconds=session_ttl)
        _ = Session.add(db, session_id, user.user_id, expires_at)
        logger.info("User: {} logged in, session_id: {}".format(
            user, session_id)
        )
        return user, session_id

    @classmethod
    def logout(cls, session):
        db = inject.instance('db')
        _ = Session.delete(db, session)
        logger.info("Session {} deleted", session)
