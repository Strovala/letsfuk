import os
import json
import bcrypt
import uuid
from flask import Flask, jsonify, request, make_response, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy.exc import IntegrityError
from config import Config

app = Flask(__name__)
sess = Session()
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import User


@app.route('/auth/login', methods=["POST"])
def login():
    body = json.loads(request.data)
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
    session_id = uuid.uuid4()
    session["session_id"] = session_id
    return jsonify({
        "user": user.to_dict(),
        "session_id": session_id
    })


# # Check if user is already logged in
# # session_id = session.get("session_id")
# # if session_id is not None:
# #     return jsonify({
# #         "session_id": session_id
# #     })

@app.route('/auth/logout', methods=["POST"])
def logout():
    session_id = session.get("session_id")
    if session_id is not None:
        del session["session_id"]
    return jsonify({})


@app.route('/users', methods=["POST"])
def register():
    body = json.loads(request.data)
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


@app.route('/users/<int:user_id>', methods=["GET"])
def get_user_by_id(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify("Entity not found"), 404
    return jsonify(user.to_dict())


@app.route('/users/<username>', methods=["GET"])
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify("Entity not found"), 404
    return jsonify(user.to_dict())


if __name__ == '__main__':
    app.secret_key = Config.SECRET_KEY
    sess.init_app(app)
    app.run()
