import inject
from sqlalchemy import (
    func,
    Column, UniqueConstraint, DateTime,
    Text, ForeignKey, Integer, String, Numeric
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.hybrid import hybrid_method
from tornado_sqlalchemy import declarative_base

Base = declarative_base()


def commit(db):
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise e


class Station(Base):
    __tablename__ = 'stations'
    __table_args__ = (
        UniqueConstraint('latitude', 'longitude', name='location'),
    )

    id = Column(Integer, ForeignKey('receivers.id'), primary_key=True)
    _latitude = Column(
        Numeric(10, 6), index=True, nullable=False,
        name='latitude'
    )
    _longitude = Column(
        Numeric(10, 6), index=True, nullable=False,
        name='longitude'
    )

    @property
    def station_id(self):
        db = inject.instance('db')
        receiver = db.query(Receiver).filter(Receiver.id == self.id).first()
        return receiver.receiver_id

    @classmethod
    def add(cls, db, station_id, lat, lon):
        receiver = Receiver.add(db, station_id)
        station = cls(
            id=receiver.id,
            _latitude=lat,
            _longitude=lon
        )
        db.add(station)
        commit(db)
        return station

    @hybrid_method
    def distance(self, lat, lon):
        return func.sqrt(
            (self._latitude - lat)*(self._latitude - lat) +
            (self._longitude - lon)*(self._longitude - lon)
        )

    @classmethod
    def get_closest(cls, db, lat, lon):
        station = db.query(cls).group_by(cls.id).order_by(
            cls.distance(lat, lon)
        ).first()
        return station

    @property
    def latitude(self):
        return float(self._latitude)

    @property
    def longitude(self):
        return float(self._longitude)

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

    id = Column(Integer, ForeignKey('receivers.id'), primary_key=True)
    username = Column(String, index=True, nullable=False, unique=True)
    email = Column(String, index=True, nullable=False, unique=True)
    password = Column(String, nullable=False)

    @property
    def user_id(self):
        db = inject.instance('db')
        receiver = db.query(Receiver).filter(Receiver.id == self.id).first()
        return receiver.receiver_id

    @classmethod
    def add(cls, db, user_id, username, email, password):
        receiver = Receiver.add(db, user_id)
        user = cls(
            id=receiver.id,
            username=username,
            password=password,
            email=email
        )
        db.add(user)
        commit(db)
        return user

    @classmethod
    def query_by_user_id(cls, db, user_id):
        return db.query(cls).join(Receiver).filter(
            Receiver.receiver_id == user_id
        ).first()

    @classmethod
    def query_by_username(cls, db, username):
        return db.query(cls).filter(
            cls.username == username
        ).first()

    @classmethod
    def query_by_email(cls, db, email):
        return db.query(cls).filter(
            cls.email == email
        ).first()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
        }

    def __repr__(self):
        return (
            '<id: {} user_id: {} username: {} email: {}>'.format(
                self.id, self.user_id, self.username, self.email
            )
        )


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID, index=True, nullable=False, unique=True)
    user_id = Column(
        UUID, ForeignKey('receivers.receiver_id'), nullable=False, unique=True
    )
    expires_at = Column(DateTime, nullable=False)

    @classmethod
    def update_expiring(cls, db, session, expires_at):
        session.expires_at = expires_at
        commit(db)
        return session

    @classmethod
    def add(cls, db, session_id, user_id, expires_at):
        sess = cls(
            session_id=session_id,
            user_id=user_id,
            expires_at=expires_at
        )
        db.add(sess)
        commit(db)
        return sess

    @classmethod
    def delete(cls, db, session):
        db.delete(session)
        commit(db)
        return session

    @classmethod
    def query_by_user_id(cls, db, user_id):
        return db.query(cls).filter(
            cls.user_id == user_id
        ).first()

    @classmethod
    def query_by_session_id(cls, db, session_id):
        return db.query(cls).filter(
            cls.session_id == session_id
        ).first()

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


class Subscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(
        UUID, ForeignKey('receivers.receiver_id'), nullable=False
    )
    user_id = Column(
        UUID, ForeignKey('receivers.receiver_id'), index=True,
        nullable=False, unique=True
    )

    @classmethod
    def get_users_for_station(cls, db, station_id):
        user_ids = db.query(cls).filter(cls.station_id == station_id).first()
        users = db.query(User).filter(User.user_id.in_(user_ids))
        return users

    @classmethod
    def get_station_for_user(cls, db, user_id):
        station_id = db.query(cls).filter(cls.user_id == user_id).first()
        station = db.query(Station).filter(
            Station.station_id == station_id
        ).first()
        return station

    @classmethod
    def add(cls, db, station_id, user_id):
        subscriber = cls(
            station_id=station_id,
            user_id=user_id
        )
        db.add(subscriber)
        commit(db)
        return subscriber

    def to_dict(self):
        return {
            "station_id": self.station_id,
            "user_id": self.user_id,
        }

    def __repr__(self):
        return (
            '<id: {} station_id: {} user_id: {}>'.format(
                self.id, self.station_id, self.user_id
            )
        )


class Receiver(Base):
    __tablename__ = 'receivers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    receiver_id = Column(UUID, index=True, nullable=False, unique=True)

    @classmethod
    def add(cls, db, receiver_id):
        receiver = Receiver(
            receiver_id=receiver_id
        )
        db.add(receiver)
        commit(db)
        return receiver


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(UUID, index=True, nullable=False, unique=True)
    receiver_id = Column(
        UUID, ForeignKey('receivers.receiver_id'), nullable=False
    )
    sender_id = Column(
        UUID, ForeignKey('receivers.receiver_id'), nullable=False
    )
    sent_at = Column(DateTime, nullable=False)
    text = Column(String(600), nullable=False)

    @classmethod
    def add(cls, db, message_id, receiver_id, sender_id, text, sent_at):
        message = Message(
            message_id=message_id,
            receiver_id=receiver_id,
            sender_id=sender_id,
            text=text,
            sent_at=sent_at
        )
        db.add(message)
        commit(db)
        return message

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "receiver_id": self.receiver_id,
            "sender_id": self.sender_id,
        }

    def __repr__(self):
        return (
            '<id: {} message_id: {} receiver_id: {} sender_id: {}>'.format(
                self.id, self.message_id, self.receiver_id, self.sender_id
            )
        )
