from datetime import datetime

from sqlalchemy import FetchedValue

from main import db


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
    id = db.Column(db.Integer, db.Sequence("families_id_seq", start=1, increment=1), server_default=FetchedValue(),
                   autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    creation = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __init__(self, family_id, family_group, family_name):
        self.id = family_id
        self.group = family_group
        self.name = family_name

    def __repr__(self):
        return "<id {}>".format(self.id)


class FamilyGroup(db.Model):
    """
    Specifies how family-group relationships are defined in the database

    @type  family_id: int
    @param family_id: family's ID
    @type  group_id: int
    @param group_id: ID of the group where the family belongs
    """

    __tablename__ = "families_groups"
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"), primary_key=True, unique=False, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), unique=False, nullable=False)
    confirmed = db.Column(db.Boolean, default=False, unique=False, nullable=False)

    def __init__(self, family_id, group_id, confirmed=False):
        self.family_id = family_id
        self.group_id = group_id
        self.confirmed = confirmed

    def __repr__(self):
        return "<id {}>".format(self.family_id)
