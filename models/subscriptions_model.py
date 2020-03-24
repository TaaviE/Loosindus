# coding=utf-8
# Copyright: Taavi Eomäe 2017-2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Contains all models related to subscription subsystem
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, TIMESTAMP

from main import db
from models.users_model import User


class Subscription(db.Model):
    """
    Specifies which users have subscriptions and if they're valid
    """
    __tablename__ = "subscriptions"

    user_id: int = Column(Integer, ForeignKey(User.id), primary_key=True, nullable=False)
    type_id: int = Column(Integer, ForeignKey("subscription_types.id"), nullable=False)
    until: datetime = Column(TIMESTAMP, nullable=False)
    active: bool = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return "<id {}>".format(self.user_id)

    def __str__(self):
        return "{\"user_id\": {user_id}, \"type\": {type}, \"until\": \"{until}\", \"active\": {active}}".format(
            user_id=self.user_id,
            type=self.type,
            until=self.until,
            active=str(self.active).lower()
        )
