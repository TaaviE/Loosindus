# coding=utf-8
"""
Specifies how groups of people are stored in a database

"""
from sqlalchemy import FetchedValue, VARCHAR, BigInteger, Column

from main import db


class Group(db.Model):
    """
    Specifies how groups are modeled in the database

    @type  group_id: int
    @param group_id: group's ID
    @type  group_name: str
    @param group_name: 255 letter name of the group
    """
    __tablename__ = "groups"

    id = Column(BigInteger, server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    name = Column(VARCHAR(255), nullable=True)
    description = Column(VARCHAR(255), nullable=True)

    def __init__(self, group_id, group_name):
        self.id = group_id
        self.name = group_name

    def __repr__(self):
        return "<id {}>".format(self.id)
