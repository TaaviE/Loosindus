# coding=utf-8
"""
Initializes a few lookup tables for quick name to ID
"""
from sqlalchemy import BigInteger, Column, FetchedValue, Integer, VARCHAR

from main import db


class AuditEventType(db.Model):
    """
    Specifies how event types are stored in the database
    """
    __tablename__ = "audit_events_types"

    id: int = Column(BigInteger(), server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    name: str = Column(VARCHAR(), nullable=False)
    description: str = Column(VARCHAR(1024), nullable=False)


class ShufflingEventType(db.Model):
    """
    Specifies how event types are stored in the database
    """

    __tablename__ = "event_types"

    id: int = Column(BigInteger(), server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    name: str = Column(VARCHAR(), nullable=True)


class SubscriptionType(db.Model):
    """
    Specifies different types of subscriptions
    """
    __tablename__ = "subscription_types"

    id: int = Column(BigInteger(), server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    name: str = Column(VARCHAR(255), nullable=False)

    def __repr__(self):
        return "<id {}>".format(self.user_id)

    def __str__(self):
        return "{\"id\": {id}, \"name\": \"{name}\"}".format(id=self.id, name=self.name)


class WishlistStatusType(db.Model):
    """
    Specifies the different states a note can be in
    """
    __tablename__ = "wishlist_status_types"
    id: int = Column(Integer(), server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    name: str = Column(VARCHAR(255), nullable=False)


event_type_to_id: dict = {}
for event_type in ShufflingEventType.query.all():
    event_type_to_id[event_type.name.lower().replace(" ", "_")] = event_type.id

subscription_type_to_id: dict = {}
for subscription_type in SubscriptionType.query.all():
    subscription_type_to_id[subscription_type.name.lower().replace(" ", "_")] = subscription_type.id

audit_event_type_to_id: dict = {}
for event_type in AuditEventType.query.all():
    audit_event_type_to_id[event_type.name.lower().replace(" ", "_")] = event_type.id

wishlist_status_to_id = {}
for status in WishlistStatusType.query.all():
    wishlist_status_to_id[status.name.lower().replace(" ", "_")] = status.id
