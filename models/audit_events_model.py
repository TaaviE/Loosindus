# coding=utf-8
"""
Contains all the models related to logging user actions
"""

from datetime import datetime

from sqlalchemy import BigInteger, Column, FetchedValue, ForeignKey, Integer, TIMESTAMP, VARCHAR

from main import db
from models.groups_model import Group


class AuditEventType(db.Model):
    """
    Specifies how event types are stored in the database
    """

    __tablename__ = "audit_events_types"

    id: int = Column(BigInteger(), server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    name: str = Column(VARCHAR(), nullable=False)
    description: str = Column(VARCHAR(1024), nullable=False)


audit_event_type_to_id = {}
for event_type in AuditEventType.query.all():
    audit_event_type_to_id[event_type.name.lower().replace(" ", "_")] = event_type.id


class AuditEvent(db.Model):
    """
    Specifies how audit events are stored in the database
    """

    __tablename__ = "audit_events"

    event_type_id: int = Column(Integer(), ForeignKey(AuditEventType.id), nullable=False)
    when: datetime = Column(TIMESTAMP(), server_default=FetchedValue(), nullable=False)
    id: int = Column(BigInteger(), server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    event_at: datetime = Column(TIMESTAMP(), nullable=True)
    user_id: int = Column(Integer(), ForeignKey(Group.id), nullable=False)
    ip: str = Column(VARCHAR(255), nullable=False)

    def __str__(self):
        return "{" \
               "\"id\": {id}, " \
               "\"created_at\": \"{created_at}\", " \
               "\"name\": \"{name}\", " \
               "\"event_at\": \"{event_at}\", " \
               "\"group_id\": {group_id}, " \
               "\"event_type\": {event_type}" \
               "}".format(
            id=self.id,
            created_at=self.created_at,
            name=self.name,
            event_at=self.year,
            group_id=self.group,
            event_type=self.event_type
        )

    def __hash__(self):
        return hash(str(self))
