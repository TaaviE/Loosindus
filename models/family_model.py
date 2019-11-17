# coding=utf-8
"""
Contains all the models related to families in the system
"""
from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import BigInteger, Boolean, Column, DateTime, FetchedValue, ForeignKey, Integer, String, VARCHAR
from sqlalchemy.orm import backref, relationship

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

    families: List[Family] = relationship(
        "Family",
        secondary="families_groups",
        backref=backref("Group", lazy="dynamic")
    )

    admins: List[User] = relationship(
        "User",
        secondary="groups_admins",
        backref="groups_administered"
    )

    events: List[ShufflingEvent] = relationship("ShufflingEvent")

    def __init__(self, group_id: int, group_name: str):
        self.id = group_id
        self.name = group_name

    def __repr__(self):
        return "<id {}>".format(self.id)


class Family(db.Model):
    """
    Specifies how families are modeled in the database
    """

    __tablename__ = "families"
    id: int = Column(BigInteger, server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    name: str = Column(String(255), nullable=False)
    creation: datetime = Column(DateTime, nullable=False, default=datetime.now())

    groups: List[Group] = relationship(
        Group,
        secondary="families_groups",
        backref=backref("Family", lazy="dynamic")
    )

    members: List[User] = relationship(
        "User",
        secondary="users_families"
    )

    admins: List[User] = relationship(
        "User",
        secondary="families_admins",
        backref=backref("User", lazy="dynamic")
    )

    def __repr__(self):
        return "<id {}>".format(self.id)


class FamilyGroup(db.Model):
    """
    Specifies how family-group relationships are defined in the database
    """

    __tablename__ = "families_groups"
    family_id: int = Column(Integer, ForeignKey(Family.id), primary_key=True, unique=False, nullable=False)
    group_id: int = Column(Integer, ForeignKey(Group.id), unique=False, nullable=False)
    confirmed: bool = Column(Boolean, default=False, unique=False, nullable=False)

    def __repr__(self):
        return "<id {}>".format(self.family_id)


class FamilyAdmin(db.Model):
    """
    Specifies how user-family administration relationships are modeled in the database
    """

    __tablename__ = "families_admins"
    user_id: int = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    family_id: int = Column(Integer, ForeignKey(Family.id), primary_key=True, nullable=False)
    admin: bool = Column(Boolean, nullable=False)
    confirmed: bool = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return "<user_id {}>".format(self.user_id)


class GroupAdmin(db.Model):
    """
    Specifies how user-group-admin relationships are modeled in the database
    """

    __tablename__ = "groups_admins"
    user_id: int = Column(Integer, ForeignKey("users.id"), primary_key=True, unique=True, nullable=False)
    group_id: int = Column(Integer, ForeignKey(Group.id), primary_key=True, nullable=False)
    admin: bool = Column(Boolean, nullable=False)
    confirmed: bool = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return "<user_id {}, group_id {}, admin {}>".format(self.user_id, self.group_id, self.admin)
