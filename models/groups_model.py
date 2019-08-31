# coding=utf-8
"""
Specifies how groups of people are stored in a database

"""
from sqlalchemy import BigInteger, Column, FetchedValue, VARCHAR

from main import db


class Group(db.Model):
    """
    Specifies how groups are modeled in the database

    @param group_id: group's ID
    @param group_name: 255 letter name of the group
    """
    __tablename__ = "groups"

    id: int = Column(BigInteger, server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    name: str = Column(VARCHAR(255), nullable=True)
    description: str = Column(VARCHAR(255), nullable=True)

    def __init__(self, group_id: int, group_name: str):
        self.id = group_id
        self.name = group_name

    def __repr__(self):
        return "<id {}>".format(self.id)