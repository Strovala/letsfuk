import inject
from sqlalchemy import (
    Column, ForeignKey, Integer, String
)

from letsfuk.db import Base, commit
from letsfuk.db.receiver import Receiver



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
