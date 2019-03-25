import uuid
import bcrypt
import datetime
from flask import Blueprint, jsonify
from sqlalchemy.exc import IntegrityError
from letsfuk import app, db
from letsfuk.decorators import check_session, resolve_body, view_wrapper
from letsfuk.database.models import User, Session

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=["POST"])
@view_wrapper()
@resolve_body()
def login(request):
    username = request.body.get("username")
    password = request.body.get("password")
    if password is None:
        return jsonify("Password can't be empty"), 400
    email = request.body.get("email")
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


@auth.route('/logout', methods=["POST"])
@view_wrapper()
@check_session()
def logout(request):
    db.session.delete(request.session)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        db.session.remove()
        return jsonify("Error occured :{}".format(e)), 500
    return jsonify("You are successfully logged out"), 200
