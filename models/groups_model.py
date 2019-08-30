# coding=utf-8
"""
Specifies how groups of people are stored in a database

"""
from sqlalchemy import FetchedValue, VARCHAR, BigInteger, Boolean, Integer, ForeignKey, Column

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


class UserGroupAdmin(db.Model):
    """
    Specifies how user-group-admin relationships are modeled in the database

    @type  user_id: int
    @param user_id: user's ID
    @type  group_id: int
    @param group_id: family_id where the family belongs ID
    @type  admin: bool
    @param admin: if the user is the adming of the group
    """

    __tablename__ = "users_groups_admins"
    user_id: int = Column(Integer, ForeignKey("user.id"), primary_key=True, unique=True, nullable=False)
    group_id: int = Column(Integer, ForeignKey("groups.id"), primary_key=True, nullable=False)
    admin: bool = Column(Boolean, nullable=False)
    confirmed: bool = Column(Boolean, nullable=False, default=False)

    def __init__(self, user_id: int, group_id: int, admin: bool):
        self.user_id = user_id
        self.group_id = group_id
        self.admin = admin

    def __repr__(self):
        return "<user_id {}, group_id {}>".format(self.user_id, self.group_id)