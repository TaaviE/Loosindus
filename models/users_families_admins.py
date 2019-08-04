# coding=utf-8
"""
Contains the model how users are related to families
"""
from sqlalchemy import Integer, ForeignKey, Boolean, Column

from main import db
from models.family_model import Family
from models.users_model import User


class UserFamilyAdmin(db.Model):
    """
    Specifies how user-family-admin relationships are modeled in the database

    @type  user_id: int
    @param user_id: user's ID
    @type  family_id: int
    @param family_id: family_id where the family belongs ID
    @type  admin: bool
    @param admin: if the user is the admin of the family
    """

    __tablename__ = "users_families_admins"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey("families.id"), primary_key=True, nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, user_id, family_id, admin):
        self.user_id = user_id
        self.family_id = family_id
        self.admin = admin

    def __repr__(self):
        return "<user_id {}>".format(self.user_id)
