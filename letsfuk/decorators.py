import datetime
import json
from functools import wraps
from json import JSONDecodeError

import inject
from sqlalchemy.exc import IntegrityError

from letsfuk.db.models import Session, User
from letsfuk.errors import HttpException, InternalError


class Request(object):
    def __init__(self):
        self.session = None
        self.body = None
        self.user = None


def error_handler(**kwargs):
    def dec(func):
        @wraps(func)
        def wrapper(self, *args, **kw):
            try:
                return func(self, *args, **kw)
            except HttpException as e:
                response = {
                    "status_code": e.status_code,
                    "text": e.text
                }
                return self.send_response(response, e.status_code)
        return wrapper
    return dec


def map_exception(**kwargs):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kw):
            out_of = kwargs.get('out_of', Exception)
            if not isinstance(out_of, tuple):
                out_of = tuple([out_of])
            make = kwargs.get('make', Exception)
            try:
                return func(*args, **kw)
            except out_of as e:
                raise make(str(e))
        return wrapper
    return dec


def resolve_body(**kwargs):
    def dec(func):
        @wraps(func)
        def wrapper(self, *args, **kw):
            try:
                body = json.loads(self.request.body)
            except JSONDecodeError as e:
                return self.send_response("You sent empty payload", 400)
            self.request.body = body
            return func(self, *args, **kw)
        return wrapper
    return dec


def resolve_user(**kwargs):
    def dec(func):
        @wraps(func)
        def wrapper(self, *args, **kw):
            user = User.query.filter_by(id=self.request.session.user_id)
            self.request.user = user
            return func(self, *args, **kw)
        return wrapper
    return dec


def check_session(**kwargs):
    def dec(func):
        @wraps(func)
        @map_exception(out_of=IntegrityError, make=InternalError)
        def wrapper(self, *args, **kw):
            db = inject.instance('db')
            session_id = self.request.headers.get('session-id')
            existing_session = Session.query_by_session_id(db, session_id)
            if existing_session is not None:
                # Check if session is expired
                now = datetime.datetime.now()
                if now < existing_session.expires_at:
                    # TODO: make config file
                    session_ttl = 30
                    expires_at = now + datetime.timedelta(minutes=session_ttl)
                    _ = Session.update_expiring(
                        db, existing_session, expires_at
                    )
                # session is expired
                else:
                    # logout logic
                    Session.delete(db, existing_session)
                    self.send_response(
                        "You are successfully logged out", 200
                    )
                    return
                self.request.session = existing_session
                return func(self, *args, **kw)
            self.send_response("Unauthorized", 401)
        return wrapper
    return dec
