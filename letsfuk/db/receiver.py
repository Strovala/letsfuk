from sqlalchemy import (
    Column, Integer
)
from sqlalchemy.dialects.postgresql import UUID

from letsfuk.db import Base, commit


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
