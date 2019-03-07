from app import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID


class Station(db.Model):
    __tablename__ = 'stations'
    __table_args__ = (
        UniqueConstraint('latitude', 'longitude', name='location'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    station_id = db.Column(UUID, index=True, nullable=True, unique=True)
    latitude = db.Column(db.String(), nullable=False)
    longitude = db.Column(db.String(), nullable=False)

    def __init__(self, latitude, longitude, uuid=None):
        self.latitude = latitude
        self.longitude = longitude
        if uuid is not None:
            self.uuid = uuid

    def __repr__(self):
        return (
            '<id {} lat{} lon{} uuid{}>'.format(
                self.id, self.latitude, self.longitude, self.uuid
            )
        )


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, index=True, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }
