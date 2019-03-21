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

    def to_dict(self):
        return {
            "station_id": self.station_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

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
    email = db.Column(db.String, index=True, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
        }

    def __repr__(self):
        return (
            '<id: {} username: {} email: {}>'.format(
                self.id, self.username, self.email
            )
        )


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(UUID, index=True, nullable=False, unique=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True
    )
    expires_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "expires_at": self.expires_at,
        }

    def __repr__(self):
        return (
            '<id: {} session_id: {} expires_at: {}>'.format(
                self.id, self.session_id, self.expires_at
            )
        )
