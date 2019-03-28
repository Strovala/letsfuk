from sqlalchemy import (
    Column, ForeignKey, Integer
)
from sqlalchemy.dialects.postgresql import UUID

from letsfuk.db import Base, commit


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

