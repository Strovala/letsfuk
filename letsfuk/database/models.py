from sqlalchemy import Column, UniqueConstraint, DateTime, ForeignKey, Integer, \
    String
from sqlalchemy.dialects.postgresql import UUID
from tornado_sqlalchemy import declarative_base

Base = declarative_base


class Station(Base):
    __tablename__ = 'stations'
    __table_args__ = (
        UniqueConstraint('latitude', 'longitude', name='location'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(UUID, index=True, nullable=True, unique=True)
    latitude = Column(String, nullable=False)
    longitude = Column(String, nullable=False)

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


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, index=True, nullable=False, unique=True)
    email = Column(String, index=True, nullable=False, unique=True)
    password = Column(String, nullable=False)

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


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID, index=True, nullable=False, unique=True)
    user_id = Column(
        Integer, ForeignKey('users.id'), nullable=False, unique=True
    )
    expires_at = Column(DateTime, nullable=False)

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
