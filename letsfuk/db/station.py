import inject
from sqlalchemy import (
    func,
    Column, UniqueConstraint,
    ForeignKey, Integer, Numeric
)
from sqlalchemy.ext.hybrid import hybrid_method

from letsfuk.db import Base, commit
from letsfuk.db.receiver import Receiver


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

