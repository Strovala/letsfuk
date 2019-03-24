from flask import jsonify
from sqlalchemy.exc import IntegrityError

from letsfuk import app
from letsfuk.decorators import (
    check_session, resolve_body, resolve_user, view_wrapper,
    map_exception
)
from letsfuk.errors import BadRequest, InternalError, Conflict, NotFound
from letsfuk.models import (
    User, InvalidRegistrationPayload, UserNotFound, UserAlreadyExists
)


@app.route('/users', methods=["POST"])
@view_wrapper()
@map_exception(out_of=InvalidRegistrationPayload, make=BadRequest)
@map_exception(out_of=UserAlreadyExists, make=Conflict)
@map_exception(out_of=IntegrityError, make=InternalError)
@resolve_body()
def register(request):
    User.validate_registration_payload(request.body)
    user = User.add(request.body)
    return jsonify(user.to_dict()), 201


@app.route('/users/<username>', methods=["GET"])
@view_wrapper()
@map_exception(out_of=UserNotFound, make=NotFound)
@check_session()
def get_user_by_username(request, username):
    user = User.get(username)
    return jsonify(user.to_dict())


@app.route('/stations/subscribe', methods=["POST"])
@view_wrapper()
@check_session()
@resolve_body()
@resolve_user()
def subscribe_to_station(request):
    lat = request.body.get("lat")
    lon = request.body.get("lon")
    if lat is None or lon is None:
        return jsonify("You need to provide both latitude and longitude"), 400
