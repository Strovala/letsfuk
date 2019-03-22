import datetime
import os
import json
from functools import wraps
from json import JSONDecodeError

import bcrypt
import uuid
from flask import Flask, jsonify, session
from flask import request as flask_request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import User, Session


def _make_or_get_request_object(*args):
    if len(args) > 0:
        request = args[0]
    else:
        request = Request()
    return request


class Request(object):
    def __init__(self):
        self.session = None
        self.body = None
        self.user = None


def resolve_body(**kwargs):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kw):
            request = _make_or_get_request_object(*args)
            try:
                body = json.loads(flask_request.data)
            except JSONDecodeError as e:
                return jsonify("You sent empty payload"), 400
            request.body = body
            return func(*args, **kw)
        return wrapper
    return dec


def resolve_user(**kwargs):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kw):
            request = _make_or_get_request_object(*args)
            user = User.query.filter_by(id=request.session.user_id)
            request.user = user
            return func(*args, **kw)
        return wrapper
    return dec


def check_session(**kwargs):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kw):
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
                request = _make_or_get_request_object(*args)
                request.session = existing_session
                return func(request, *args, **kw)
            return jsonify("Unauthorized"), 401
        return wrapper
    return dec


@app.route('/auth/login', methods=["POST"])
def login():
    body = json.loads(flask_request.data)
    username = body.get("username")
    password = body.get("password")
    if password is None:
        return jsonify("Password can't be empty"), 400
    email = body.get("email")
    user = None
    if email is not None:
        user = User.query.filter_by(email=email).first()
    elif username is not None:
        user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify("Wrong credentials or password"), 400
    encoded_password = password.encode()
    encoded_hashed_password = user.password.encode()
    matching = bcrypt.checkpw(encoded_password, encoded_hashed_password)
    if not matching:
        return jsonify("Wrong credentials or password"), 400
    existing_session = Session.query.filter_by(user_id=user.id).first()
    if existing_session is not None:
        return jsonify({
            "user": user.to_dict(),
            "session_id": existing_session.session_id
        })
    session_id = str(uuid.uuid4())
    session_ttl = app.config.get('SESSION_TTL', 30)
    now = datetime.datetime.now()
    expires_at = now + datetime.timedelta(minutes=session_ttl)
    sess = Session(
        session_id=session_id,
        user_id=user.id,
        expires_at=expires_at
    )
    db.session.add(sess)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        db.session.remove()
        return jsonify("Error occured :{}".format(e)), 500
    return jsonify({
        "user": user.to_dict(),
        "session_id": session_id
    })


@app.route('/auth/logout', methods=["POST"])
@check_session()
def logout(sess):
    db.session.delete(sess)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        db.session.remove()
        return jsonify("Error occured :{}".format(e)), 500
    return jsonify("You are successfully logged out"), 200


@app.route('/users', methods=["POST"])
@resolve_body()
def register():
    body = json.loads(flask_request.data)
    username = body.get("username")
    password = body.get("password")
    email = body.get("email")
    if password is None or password == "":
        return jsonify("Password can't be empty"), 400
    encoded_password = password.encode()
    hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
    decoded_hashed_password = hashed_password.decode()
    user = User(
        username=username, password=decoded_hashed_password, email=email
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        db.session.remove()
        return jsonify("Error occured :{}".format(e)), 400
    return jsonify(user.to_dict()), 201


@app.route('/users/<username>', methods=["GET"])
@check_session()
def get_user_by_username(request, username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify("Entity not found"), 404
    return jsonify(user.to_dict())


@app.route('/stations/subscribe', methods=["POST"])
@check_session()
@resolve_body()
@resolve_user()
def subscribe_to_station(request):
    lat = request.body.get("lat")
    lon = request.body.get("lon")
    if lat is None or lon is None:
        return jsonify("You need to provide both latitude and longitude"), 400


if __name__ == '__main__':
    app.run()
