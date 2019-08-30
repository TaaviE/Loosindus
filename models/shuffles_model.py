# coding=utf-8
"""
Contains all the models related to shuffles made between people
"""
from datetime import datetime

from sqlalchemy import BigInteger, Column, FetchedValue, ForeignKey, Integer

from main import db
from models.groups_model import Group
from models.users_model import User


class Shuffle(db.Model):
    """
    Specifies how pairs of people between whom gifts are made are shuffled
    """

    __tablename__ = "shuffles"

    id: int = Column(BigInteger, server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    giver: int = Column(Integer(), ForeignKey(User.id), nullable=False)
    getter: int = Column(Integer(), ForeignKey(User.id), nullable=False)
    year: int = Column(Integer(), default=datetime.now().year, nullable=False)
    group: int = Column(Integer(), ForeignKey(Group.id))

    def __str__(self):
        return "{\"id\": {id}, \"giver\": {giver}, \"getter\": {getter}, \"year\": {year}, \"group\": {group}}".format(
            id=self.id,
            giver=self.giver,
            getter=self.getter,
            year=self.year,
            group=self.group)

    def __hash__(self):
        return hash(str(self))
