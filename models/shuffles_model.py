# coding=utf-8
"""
Contains all the models related to shuffles made between people
"""
from datetime import datetime

from sqlalchemy import FetchedValue, BigInteger, Column, Integer, ForeignKey

from main import db
from models.groups_model import Group
from models.users_model import User


class Shuffle(db.Model):
    """
    Specifies how pairs of people between whom gifts are made are shuffled
    """

    __tablename__ = "shuffles"

    id = db.Column(db.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    giver = db.Column(db.Integer(), db.ForeignKey(User.id), nullable=False)
    getter = db.Column(db.Integer(), db.ForeignKey(User.id), nullable=False)
    year = db.Column(db.Integer(), default=datetime.now().year, nullable=False)
    group = db.Column(db.Integer(), db.ForeignKey(Group.id))

    def __str__(self):
        return "{\"id\": {id}, \"giver\": {giver}, \"getter\": {getter}, \"year\": {year}, \"group\": {group}}".format(
            id=self.id,
            giver=self.giver,
            getter=self.getter,
            year=self.year,
            group=self.group)

    def __hash__(self):
        return hash(str(self))
