# coding=utf-8
from sqlalchemy import Boolean, Integer, ForeignKey, Column

from main import db


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
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True, unique=True, nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True, nullable=False)
    admin = Column(Boolean, nullable=False)
    confirmed = Column(Boolean, nullable=False, default=False)

    def __init__(self, user_id, group_id, admin):
        self.user_id = user_id
        self.group_id = group_id
        self.admin = admin

    def __repr__(self):
        return "<user_id {}, group_id {}>".format(self.user_id, self.group_id)
