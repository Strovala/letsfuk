import os
import json
import bcrypt
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import User


@app.route('/', methods=["POST"])
def register():
    body = json.loads(request.data)
    username = body.get("username")
    password = body.get("password")
    email = body.get("email")
    if password is None or password == "":
        return jsonify("Password can't be empty"), 400
    encoded_password = password.encode()
    hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
    user = User(username=username, password=hashed_password, email=email)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        db.session.remove()
        return jsonify("Error occured :{}".format(e)), 400
    return jsonify(user.to_dict()), 201


@app.route('/<int:user_id>', methods=["GET"])
def get_user_by_id(user_id):
    user = User.query.filter_by(id=user_id).first()
    print(user)


@app.route('/<username>', methods=["GET"])
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    print(user)


if __name__ == '__main__':
    app.run()
