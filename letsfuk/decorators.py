import datetime
import json
from functools import wraps
from json import JSONDecodeError

from flask import request as flask_request, jsonify
from sqlalchemy.exc import IntegrityError

from letsfuk import app, db
from letsfuk.database.models import Session, User
from letsfuk.errors import HttpException


class Request(object):
    def __init__(self):
        self.session = None
        self.body = None
        self.user = None


def view_wrapper(**kwargs):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kw):
            request = Request()
            try:
                return func(request, *args, **kw)
            except HttpException as e:
                response = {
                    "status_code": e.status_code,
                    "text": e.text
                }
                return jsonify(response), e.status_code
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
        def wrapper(request, *args, **kw):
            try:
                body = json.loads(flask_request.data)
            except JSONDecodeError as e:
                return jsonify("You sent empty payload"), 400
            request.body = body
            return func(request, *args, **kw)
        return wrapper
    return dec


def resolve_user(**kwargs):
    def dec(func):
        @wraps(func)
        def wrapper(request, *args, **kw):
            user = User.query.filter_by(id=request.session.user_id)
            request.user = user
            return func(request, *args, **kw)
        return wrapper
    return dec


def check_session(**kwargs):
    def dec(func):
        @wraps(func)
        def wrapper(request, *args, **kw):
            session_id = flask_request.headers.get('session-id')
            existing_session = Session.query.filter_by(
                session_id=session_id
            ).first()
            if existing_session is not None:
                # Check if session is expired
                now = datetime.datetime.now()
                if now < existing_session.expires_at:
                    session_ttl = app.config.get('SESSION_TTL', 30)
                    expires_at = now + datetime.timedelta(minutes=session_ttl)
                    existing_session.expires_at = expires_at
                    try:
                        db.session.commit()
                    except IntegrityError as e:
                        db.session.rollback()
                        db.session.remove()
                        return jsonify("Error occured :{}".format(e)), 500
                # session is expired
                else:
                    # logout logic
                    db.session.delete(existing_session)
                    try:
                        db.session.commit()
                    except IntegrityError as e:
                        db.session.rollback()
                        db.session.remove()
                        return jsonify("Error occured :{}".format(e)), 500
                    return jsonify("You are successfully logged out"), 200
                request.session = existing_session
                return func(request, *args, **kw)
            return jsonify("Unauthorized"), 401
        return wrapper
    return dec
