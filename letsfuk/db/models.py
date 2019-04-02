from sqlalchemy import (
    Column, UniqueConstraint, DateTime, ForeignKey, Integer, String, Numeric,
    func, or_, and_, asc, desc
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_method

from letsfuk.db import commit, Base


class Station(Base):
    __tablename__ = 'stations'
    __table_args__ = (
        UniqueConstraint('latitude', 'longitude', name='location'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(UUID, index=True, nullable=False, unique=True)
    _latitude = Column(
        Numeric(10, 6), index=True, nullable=False,
        name='latitude'
    )
    _longitude = Column(
        Numeric(10, 6), index=True, nullable=False,
        name='longitude'
    )

    @classmethod
    def query_by_station_id(cls, db, station_id):
        return db.query(cls).filter(
            cls.station_id == station_id
        ).first()

    @classmethod
    def add(cls, db, station_id, lat, lon):
        station = cls(
            station_id=station_id,
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

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID, index=True, nullable=False, unique=True)
    username = Column(String, index=True, nullable=False, unique=True)
    email = Column(String, index=True, nullable=False, unique=True)
    password = Column(String, nullable=False)

    @classmethod
    def add(cls, db, user_id, username, email, password):
        user = cls(
            user_id=user_id,
            username=username,
            password=password,
            email=email
        )
        db.add(user)
        commit(db)
        return user

    @classmethod
    def query_by_user_id(cls, db, user_id):
        return db.query(cls).filter(
            cls.user_id == user_id
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
        UUID, ForeignKey('users.user_id'), nullable=False, unique=True
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
    station_id = Column(UUID, ForeignKey('stations.station_id'), nullable=False)
    user_id = Column(
        UUID, ForeignKey('users.user_id'), index=True,
        nullable=False, unique=True
    )

    @classmethod
    def get_users_for_station(cls, db, station_id):
        user_ids = db.query(cls).filter(cls.station_id == station_id).first()
        users = db.query(User).filter(User.user_id.in_(user_ids))
        return users

    @classmethod
    def get_station_for_user(cls, db, user_id):
        station = db.query(cls).filter(cls.user_id == user_id).first()
        station = db.query(Station).filter(
            Station.station_id == station.station_id
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


class PrivateChat(Base):
    __tablename__ = 'private_chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(UUID, index=True, nullable=False, unique=True)
    receiver_id = Column(
        UUID, ForeignKey('users.user_id'), nullable=True
    )
    sender_id = Column(
        UUID, ForeignKey('users.user_id'), nullable=True
    )
    sent_at = Column(DateTime, nullable=False)
    text = Column(String(600), nullable=False)

    @classmethod
    def add(
            cls, db, message_id, receiver_id, sender_id, text, sent_at
    ):
        message = PrivateChat(
            message_id=message_id,
            receiver_id=receiver_id,
            sender_id=sender_id,
            text=text,
            sent_at=sent_at
        )
        db.add(message)
        commit(db)
        return message

    @classmethod
    def get(cls, db, receiver_id, sender_id, offset, limit):
        private_chat = db.query(cls).filter(
            or_(
                and_(
                    cls.receiver_id == receiver_id,
                    cls.sender_id == sender_id,
                ),
                and_(
                    cls.receiver_id == sender_id,
                    cls.sender_id == receiver_id,
                ),
            )
        ).order_by(asc(cls.sent_at)).offset(offset).limit(limit).all()
        return private_chat

    @classmethod
    def get_user_ids_for_user_id(cls, db, user_id, offset, limit):
        user_ids_tuple = db.query(cls.receiver_id, cls.sender_id).filter(
            or_(
                cls.receiver_id == user_id,
                cls.sender_id == user_id,
            )
        ).order_by(desc(cls.sent_at)).all()
        user_ids = []
        for receiver_id, sender_id in user_ids_tuple:
            if receiver_id != user_id:
                if receiver_id not in user_ids:
                    user_ids.append(receiver_id)
            elif sender_id != user_id:
                if sender_id not in user_ids:
                    user_ids.append(sender_id)
        end = limit + offset
        if end > len(user_ids):
            end = len(user_ids)
        if offset >= len(user_ids):
            user_ids = []
        else:
            user_ids = user_ids[offset:end]
        return user_ids

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "receiver_id": self.receiver_id,
            "sender_id": self.sender_id,
            "sent_at": str(self.sent_at),
            "text": self.text
        }

    def __repr__(self):
        return (
            '<id: {} message_id: {} receiver_id: {} sender_id: {}>'.format(
                self.id, self.message_id, self.receiver_id, self.sender_id
            )
        )


class StationChat(Base):
    __tablename__ = 'station_chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(UUID, index=True, nullable=False, unique=True)
    receiver_id = Column(
        UUID, ForeignKey('stations.station_id'), nullable=True
    )
    sender_id = Column(
        UUID, ForeignKey('users.user_id'), nullable=True
    )
    sent_at = Column(DateTime, nullable=False)
    text = Column(String(600), nullable=False)

    @classmethod
    def add(
            cls, db, message_id, receiver_id, sender_id, text, sent_at
    ):
        message = StationChat(
            message_id=message_id,
            receiver_id=receiver_id,
            sender_id=sender_id,
            text=text,
            sent_at=sent_at
        )
        db.add(message)
        commit(db)
        return message

    @classmethod
    def get(cls, db, receiver_id, offset, limit):
        messages = db.query(cls).filter(
            cls.receiver_id == receiver_id
        ).order_by(asc(cls.sent_at)).offset(offset).limit(limit).all()
        return messages

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "receiver_id": self.receiver_id,
            "sender_id": self.sender_id,
            "sent_at": str(self.sent_at),
            "text": self.text
        }

    def __repr__(self):
        return (
            '<id: {} message_id: {} receiver_id: {} sender_id: {}>'.format(
                self.id, self.message_id, self.receiver_id, self.sender_id
            )
        )
