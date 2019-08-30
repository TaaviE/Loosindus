# coding=utf-8
"""
Contains all the models related to families in the system
"""
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, FetchedValue, ForeignKey, Integer, String

from main import db
from models.groups_model import Group


class Family(db.Model):
    """
    Specifies how families are modeled in the database

    @type  family_id: int
    @param family_id: family's ID
    @type  family_group: int
    @param family_group: group where the family belongs ID
    @type  family_name: str
    @param family_name: 255 letter name of the group
    """

    __tablename__ = "families"
    id = Column(BigInteger, server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    creation = Column(DateTime, nullable=False, default=datetime.now())

    def __init__(self, family_id, family_group, family_name):
        self.id = family_id
        self.group = family_group
        self.name = family_name

    def __repr__(self):
        return "<id {}>".format(self.id)


class FamilyGroup(db.Model):
    """
    Specifies how family-group relationships are defined in the database

    @param family_id: family's ID
    @param group_id: ID of the group where the family belongs
    @param confirmed: if the family has been authorized to be in the group
    """

    __tablename__ = "families_groups"
    family_id: int = Column(Integer, ForeignKey(Family.id), primary_key=True, unique=False, nullable=False)
    group_id: int = Column(Integer, ForeignKey(Group.id), unique=False, nullable=False)
    confirmed: bool = Column(Boolean, default=False, unique=False, nullable=False)

    def __init__(self, family_id: int, group_id: int, confirmed: bool = False):
        self.family_id = family_id
        self.group_id = group_id
        self.confirmed = confirmed

    def __repr__(self):
        return "<id {}>".format(self.family_id)
