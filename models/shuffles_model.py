# coding=utf-8
"""
Contains all the models related to shuffles made between people
"""

from sqlalchemy import Column, ForeignKey, Integer

from main import db
from models.events_model import ShufflingEvent
from models.users_model import User


class Shuffle(db.Model):
    """
    Specifies pairs of people between whom gifts are made and in which event
    """

    __tablename__ = "shuffles"

    giver: int = Column(Integer(), ForeignKey(User.id), primary_key=True, unique=False, nullable=False)
    getter: int = Column(Integer(), ForeignKey(User.id), primary_key=True, unique=False, nullable=False)
    event_id: int = Column(Integer(), ForeignKey(ShufflingEvent.id), primary_key=True, unique=False, nullable=False)

    def __str__(self):
        return "{\"id\": {id}, \"giver\": {giver}, \"getter\": {getter}, \"year\": {year}, \"event\": {event}}".format(
            id=self.id,
            giver=self.giver,
            getter=self.getter,
            year=self.year,
            event=self.event)

    def __hash__(self):
        return hash(str(self))
