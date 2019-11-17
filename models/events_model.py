# coding=utf-8
"""
Contains all the models related to events organized in one specific group
"""
from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import BigInteger, Boolean, Column, FetchedValue, ForeignKey, Integer, TIMESTAMP, VARCHAR
from sqlalchemy.orm import relationship

from main import db
from models.family_model import Group


class ShufflingEvent(db.Model):
    """
    Specifies how events are stored in the database
    """
    __tablename__ = "events"

    id: int = Column(BigInteger(), server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    created_at: datetime = Column(TIMESTAMP(), server_default=FetchedValue(), nullable=False)
    name: str = Column(VARCHAR(255), nullable=False)
    event_at: datetime = Column(TIMESTAMP(), nullable=True)
    group_id: int = Column(Integer(), ForeignKey(Group.id), nullable=False)
    event_type: int = Column(Integer(), ForeignKey("event_types.id"), nullable=False)

    admins: List[User] = relationship("User",
                                      secondary="events_admins",
                                      backref="events_administered")

    def __str__(self):
        return "{" \
               "\"id\": {id}, " \
               "\"created_at\": \"{created_at}\", " \
               "\"name\": \"{name}\", " \
               "\"event_at\": \"{event_at}\", " \
               "\"group_id\": {group_id}, " \
               "\"event_type\": {event_type}" \
               "}".format(
            id=self.id,
            created_at=self.created_at,
            name=self.name,
            event_at=self.year,
            group_id=self.group,
            event_type=self.event_type
        )

    def as_dict(self):
        """
        Returns a dictionary of the event with all relevant information
        """
        return {
            "id": self.id,
            "created_at": self.created_at,
            "name": self.name,
            "event_at": self.event_at,
            "group_id": self.group_id,
            "event_type": self.event_type,
        }

    def __hash__(self):
        return hash(str(self))


class EventAdmin(db.Model):
    """
    Specifies how user-event administration relationships are modeled in the database
    """
    __tablename__ = "events_admins"
    user_id: int = Column(Integer, ForeignKey("users.id"), primary_key=True, unique=True, nullable=False)
    event_id: int = Column(Integer, ForeignKey("events.id"), primary_key=True, nullable=False)
    admin: bool = Column(Boolean, nullable=False)
    confirmed: bool = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return "<user_id {}, group_id {}>".format(self.user_id, self.group_id)
