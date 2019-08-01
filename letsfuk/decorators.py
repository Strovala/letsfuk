import datetime
import json
import re
import inject
from functools import wraps
from json import JSONDecodeError
from sqlalchemy.exc import IntegrityError
from letsfuk.config import Config
from letsfuk.db.models import Session
from letsfuk.models.user import User
from letsfuk.errors import HttpException, InternalError, Unauthorized


class Request(object):
    def __init__(self):
        self.session = None
        self.body = None
        self.user = None


def endpoint_wrapper(**kwargs):
    def dec(func):
        @wraps(func)
        def wrapper(self, *args, **kw):
            try:
                self.request.params = dict()
                for param in self.request.arguments:
                    config = inject.instance(Config)
                    encoding = config.get('param_encoding', 'utf-8')
                    bytes_param = self.request.arguments[param][0]
                    str_param = bytes_param.decode(encoding)
                    self.request.params[param] = str_param
                response, status_code = func(self, *args, **kw)
            except HttpException as e:
                response = {
                    "status_code": e.status_code,
                    "text": e.text
                }
                status_code = e.status_code
            if status_code == 204:
                self.set_status(204)
                return
            self.send_response(response, status_code)
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
                return "You sent empty payload", 400
            self.request.body = body
            return func(self, *args, **kw)
        return wrapper
    return dec


def resolve_user(**kwargs):
    def dec(func):
        @wraps(func)
        def wrapper(self, *args, **kw):
            user = User.get(self.request.session.user_id)
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
            session_id = self.request.headers.get('session-id', '')
            from letsfuk import uuid_regex
            matching = re.match(uuid_regex, session_id)
            if not matching:
                raise Unauthorized("Unauthorized")
            existing_session = Session.query_by_session_id(db, session_id)
            if existing_session is not None:
                # Check if session is expired
                now = datetime.datetime.utcnow()
                if now < existing_session.expires_at:
                    config = inject.instance(Config)
                    session_ttl = config.get('session_ttl', 946100000)
                    expires_at = now + datetime.timedelta(seconds=session_ttl)
                    _ = Session.update_expiring(
                        db, existing_session, expires_at
                    )
                # session is expired
                else:
                    # logout logic
                    Session.delete(db, existing_session)
                    raise Unauthorized("Your session is expired")
                self.request.session = existing_session
                return func(self, *args, **kw)
            raise Unauthorized("Unauthorized")
        return wrapper
    return dec
