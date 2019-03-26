from sqlalchemy import (
    Column, UniqueConstraint, DateTime, ForeignKey, Integer, String,
    create_engine)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from tornado_sqlalchemy import declarative_base

Base = declarative_base()


class Station(Base):
    __tablename__ = 'stations'
    __table_args__ = (
        UniqueConstraint('latitude', 'longitude', name='location'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(UUID, index=True, nullable=False, unique=True)
    latitude = Column(String, index=True, nullable=False)
    longitude = Column(String, index=True, nullable=False)

    @classmethod
    def add(cls, db, station_id, lat, lon):
        station = cls(
            station_id=station_id,
            latitude=lat,
            longitude=lon
        )
        db.add(station)
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise e
        return station

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
    user_id = Column(
        Integer, ForeignKey('users.id'), nullable=False, unique=True
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
    def add(cls, db, session_id, user_id, expires_at):
        sess = cls(
            session_id=session_id,
            user_id=user_id,
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
