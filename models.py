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

    def __init__(self, latitude, longitude, uuid=None):
        self.latitude = latitude
        self.longitude = longitude
        if uuid is not None:
            self.uuid = uuid

    def __repr__(self):
        return (
            f'<id {self.id} lat{self.latitude} '
            f'lon{self.longitude} uuid{self.uuid}>'
        )
