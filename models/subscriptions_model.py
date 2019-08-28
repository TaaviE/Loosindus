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

    user_id: int = Column(Integer, ForeignKey(User.id), primary_key=True, nullable=False)
    type_id: int = Column(Integer, ForeignKey(SubscriptionType.id), nullable=False)
    until: datetime = Column(TIMESTAMP, nullable=False)
    active: bool = Column(Boolean, nullable=False, default=True)

    def __init__(self, user_id: int, type_id: int, until, active: bool = True):
        self.user_id = user_id
        self.type_id = type_id
        self.until = until
        self.active = active

    def __repr__(self):
        return "<id {}>".format(self.user_id)

    def __str__(self):
        return "{\"user_id\": {user_id}, \"type\": {type}, \"until\": \"{until}\", \"active\": {active}}".format(
            user_id=self.user_id,
            type=self.type,
            until=self.until,
            active=str(self.active).lower()
        )


class SubscriptionType(db.Model):
    """
    Specifies different types of subscriptions
    """
    __tablename__ = "subscription_types"

    id: int = Column(BigInteger(), server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    name: str = Column(VARCHAR(255), nullable=False)

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return "<id {}>".format(self.user_id)

    def __str__(self):
        return "{\"id\": {id}, \"name\": \"{name}\"}".format(id=self.id, name=self.name)
