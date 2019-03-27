from sqlalchemy import (
    Column, UniqueConstraint, DateTime, ForeignKey, Integer, String, Numeric,
    func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.hybrid import hybrid_method
from tornado_sqlalchemy import declarative_base

Base = declarative_base()


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
    def add(cls, db, station_id, lat, lon):
        station = cls(
            station_id=station_id,
            _latitude=lat,
            _longitude=lon
        )
        db.add(station)
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise e
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
    username = Column(String, index=True, nullable=False, unique=True)
    email = Column(String, index=True, nullable=False, unique=True)
    password = Column(String, nullable=False)

    @classmethod
    def add(cls, db, username, email, password):
        user = cls(
            username=username,
            password=password,
            email=email
        )
        db.add(user)
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise e
        return user

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
    username = Column(
        String, ForeignKey('users.username'), nullable=False, unique=True
    )
    expires_at = Column(DateTime, nullable=False)

    @classmethod
    def update_expiring(cls, db, session, expires_at):
        session.expires_at = expires_at
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise e
        return session

    @classmethod
    def add(cls, db, session_id, username, expires_at):
        sess = cls(
            session_id=session_id,
            username=username,
            expires_at=expires_at
        )
        db.add(sess)
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise e
        return sess

    @classmethod
    def delete(cls, db, session):
        db.delete(session)
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise e
        return session

    @classmethod
    def query_by_username(cls, db, username):
        return db.query(cls).filter(
            cls.username == username
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
    station_id = Column(UUID, nullable=False)
    username = Column(String, index=True, nullable=False, unique=True)

    @classmethod
    def get_users_for_station(cls, db, station_id):
        usernames = db.query(cls).filter(cls.station_id == station_id).first()
        users = db.query(User).filter(User.username.in_(usernames))
        return users

    @classmethod
    def get_station_for_user(cls, db, username):
        station_id = db.query(cls).filter(cls.username == username).first()
        station = db.query(Station).filter(
            Station.station_id == station_id
        ).first()
        return station

    @classmethod
    def add(cls, db, station_id, username):
        station_subscriber = cls(
            station_id=station_id,
            username=username
        )
        db.add(station_subscriber)
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise e
        return station_subscriber

    def to_dict(self):
        return {
            "station_id": self.station_id,
            "username": self.username,
        }

    def __repr__(self):
        return (
            '<id: {} station_id: {} username: {}>'.format(
                self.id, self.station_id, self.username
            )
        )
