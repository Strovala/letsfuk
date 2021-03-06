import logging

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
            (self._latitude - lat) * (self._latitude - lat) +
            (self._longitude - lon) * (self._longitude - lon)
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
            "lat": self.latitude,
            "lon": self.longitude,
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
    avatar_key = Column(String, nullable=True, unique=True)

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
    def search_by_username(cls, db, username):
        search = '{}%'.format(username)
        return db.query(cls).filter(
            func.lower(cls.username).like(search.lower())
        ).all()

    @classmethod
    def query_by_email(cls, db, email):
        return db.query(cls).filter(
            cls.email == email
        ).first()

    @classmethod
    def update_avatar(cls, db, user, avatar_key):
        user.avatar_key = avatar_key
        commit(db)
        return user

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "avatar_key": self.avatar_key
        }

    def __repr__(self):
        return (
            '<id: {} user_id: {} username: '
            '{} email: {} avatar_key: {}>'.format(
                self.id, self.user_id, self.username,
                self.email, self.avatar_key
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
    station_id = Column(
        UUID, ForeignKey('stations.station_id'), nullable=False
    )
    user_id = Column(
        UUID, ForeignKey('users.user_id'), index=True,
        nullable=False, unique=True
    )

    @classmethod
    def get(cls, db, station_id, user_id):
        subscriber = db.query(cls).filter(
            and_(
                cls.station_id == station_id,
                cls.user_id == user_id,
                )
        ).first()
        return subscriber

    @classmethod
    def get_users_for_station(cls, db, station_id):
        user_ids_tuple = db.query(cls.user_id).filter(
            cls.station_id == station_id
        ).all()
        user_ids = [user_id_tuple[0] for user_id_tuple in user_ids_tuple]
        users = db.query(User).filter(User.user_id.in_(user_ids))
        return users

    @classmethod
    def get_station_for_user(cls, db, user_id):
        subscriber = db.query(cls).filter(cls.user_id == user_id).first()
        if subscriber is None:
            return None
        station = db.query(Station).filter(
            Station.station_id == subscriber.station_id
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

    @classmethod
    def delete(cls, db, subscriber):
        db.delete(subscriber)
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
    text = Column(String(600), nullable=True)
    image_key = Column(String, nullable=True)

    @classmethod
    def add(
        cls, db, message_id, receiver_id, sender_id,
        text, image_key, sent_at
    ):
        message = PrivateChat(
            message_id=message_id,
            receiver_id=receiver_id,
            sender_id=sender_id,
            text=text,
            image_key=image_key,
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
        ).order_by(desc(cls.sent_at)).offset(offset).limit(limit).all()
        return private_chat

    @classmethod
    def get_total(cls, db, receiver_id, sender_id):
        total = db.query(cls).filter(
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
        ).count()
        return total

    @classmethod
    def get_total_chats(cls, db, user_id):
        user_ids_tuple = db.query(cls.receiver_id, cls.sender_id).filter(
            or_(
                cls.receiver_id == user_id,
                cls.sender_id == user_id,
                )
        ).all()
        user_ids = []
        for receiver_id, sender_id in user_ids_tuple:
            if receiver_id != user_id:
                if receiver_id not in user_ids:
                    user_ids.append(receiver_id)
            elif sender_id != user_id:
                if sender_id not in user_ids:
                    user_ids.append(sender_id)
        return len(user_ids)

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
            "text": self.text,
            "image_key": self.image_key
        }

    def __repr__(self):
        return (
            '<id: {} message_id: {} receiver_id: {} sender_id: {} '
            'text: {} image_key: {}>'.format(
                self.id, self.message_id, self.receiver_id, self.sender_id,
                self.text, self.image_key
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
    text = Column(String(600), nullable=True)
    image_key = Column(String, nullable=True)

    @classmethod
    def add(
        cls, db, message_id, receiver_id, sender_id,
        text, image_key, sent_at
    ):
        message = StationChat(
            message_id=message_id,
            receiver_id=receiver_id,
            sender_id=sender_id,
            text=text,
            image_key=image_key,
            sent_at=sent_at
        )
        db.add(message)
        commit(db)
        return message

    @classmethod
    def get(cls, db, receiver_id, offset, limit):
        messages = db.query(cls).filter(
            cls.receiver_id == receiver_id
        ).order_by(desc(cls.sent_at)).offset(offset).limit(limit).all()
        return messages

    @classmethod
    def get_total(cls, db, receiver_id):
        total = db.query(cls).filter(
            cls.receiver_id == receiver_id
        ).count()
        return total

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "receiver_id": self.receiver_id,
            "sender_id": self.sender_id,
            "sent_at": str(self.sent_at),
            "text": self.text,
            "image_key": self.image_key
        }

    def __repr__(self):
        return (
            '<id: {} message_id: {} receiver_id: {} '
            'sender_id: {} text: {} image_key: {}>'.format(
                self.id, self.message_id, self.receiver_id,
                self.sender_id, self.text, self.image_key
            )
        )


class Unread(Base):
    __tablename__ = 'unreads'

    id = Column(Integer, primary_key=True, autoincrement=True)
    receiver_id = Column(UUID, nullable=False)
    station_id = Column(
        UUID, ForeignKey('stations.station_id'), nullable=True
    )
    sender_id = Column(
        UUID, ForeignKey('users.user_id'), nullable=True
    )
    count = Column(Integer, nullable=False, default=0)

    @classmethod
    def add(cls, db, receiver_id, station_id=None, sender_id=None):
        if station_id is None and sender_id is None:
            return None
        unread = cls.get(db, receiver_id, station_id, sender_id)
        if unread is None:
            unread = Unread(
                receiver_id=receiver_id,
                station_id=station_id,
                sender_id=sender_id,
                count=0
            )
            db.add(unread)
        unread.count += 1
        commit(db)
        return unread

    @classmethod
    def get(cls, db, receiver_id, station_id=None, sender_id=None):
        unread = db.query(cls).filter(
            cls.receiver_id == receiver_id,
            cls.station_id == station_id,
            cls.sender_id == sender_id
        ).first()
        return unread

    @classmethod
    def reset(cls, db, receiver_id, station_id=None, sender_id=None, count=0):
        unread = cls.get(db, receiver_id, station_id, sender_id)
        if unread is None:
            return Unread()
        unread.count = count
        commit(db)
        return unread

    def to_dict(self):
        return {
            "receiver_id": self.receiver_id,
            "station_id": self.station_id,
            "sender_id": self.sender_id,
            "count": self.count
        }

    def __repr__(self):
        return (
            '<id: {} receiver_id: {} station_id: {} sender_id: {}>'.format(
                self.id, self.receiver_id, self.station_id, self.sender_id
            )
        )


class PushNotification(Base):
    __tablename__ = 'push_notifications'
    __table_args__ = (
        UniqueConstraint('endpoint', 'auth', 'p256dh', name='device_browser'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        UUID, ForeignKey('users.user_id'), nullable=False
    )
    endpoint = Column(
        String, nullable=False
    )
    auth = Column(String, nullable=False)
    p256dh = Column(String, nullable=False)

    @classmethod
    def subscribe(cls, db, user_id, endpoint, auth, p256dh):
        subscriber = cls.query_by_device_browser(db, endpoint, auth, p256dh)
        if subscriber is None:
            subscriber = PushNotification(
                user_id=user_id, endpoint=endpoint, auth=auth, p256dh=p256dh
            )
            db.add(subscriber)
        else:
            # Update new user to use this device_browser
            subscriber.user_id = user_id
        commit(db)
        return subscriber

    @classmethod
    def unsubscribe(cls, db, subscriber):
        db.delete(subscriber)
        commit(db)
        return subscriber

    @classmethod
    def get(cls, db, user_id, endpoint, auth, p256dh):
        subscriber = db.query(cls).filter(
            cls.user_id == user_id,
            cls.endpoint == endpoint,
            cls.auth == auth,
            cls.p256dh == p256dh
        ).first()
        return subscriber

    @classmethod
    def query_by_device_browser(cls, db, endpoint, auth, p256dh):
        subscriber = db.query(cls).filter(
            cls.endpoint == endpoint,
            cls.auth == auth,
            cls.p256dh == p256dh
        ).first()
        return subscriber

    @classmethod
    def query_by_user_id(cls, db, user_id):
        device_browsers = db.query(cls).filter(
            cls.user_id == user_id
        ).all()
        return device_browsers

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "endpoint": self.endpoint,
            "keys": {
                "auth": self.auth,
                "p256dh": self.p256dh
            }
        }

    def __repr__(self):
        return (
            '<id: {} user_id: {} endpoint: {} auth: {} p256dh: {}>'.format(
                self.id, self.user_id, self.endpoint, self.auth, self.p256dh
            )
        )
