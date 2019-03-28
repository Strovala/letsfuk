from sqlalchemy import (
    Column, DateTime,
    ForeignKey, Integer, String
)
from sqlalchemy.dialects.postgresql import UUID

from letsfuk.db import Base, commit


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
