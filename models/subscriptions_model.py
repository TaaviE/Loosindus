# coding=utf-8
"""
Contains all models related to subscription subsystem
"""
from sqlalchemy import ForeignKey, TIMESTAMP, Integer, FetchedValue, VARCHAR, BigInteger, Column, Boolean

from main import db
from models.users_model import User


class Subscription(db.Model):
    """
    Specifies which users have subscriptions and if they're valid
    """
    __tablename__ = "subscriptions"

    user_id = Column(Integer, ForeignKey(User.id), primary_key=True, nullable=False)
    type = Column(Integer, nullable=False)
    until = Column(TIMESTAMP, nullable=False)

    def __init__(self, user_id, type, until):
        self.user_id = user_id
        self.type = type
        self.until = until

    def __repr__(self):
        return "<id {}>".format(self.user_id)
