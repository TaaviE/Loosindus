# coding=utf-8
# Copyright: Taavi Eomäe 2017-2020
# SPDX-License-Identifier: AGPL-3.0-only
from datetime import datetime

from flask_babelex import gettext as _
from sqlalchemy import BigInteger, Column, FetchedValue, ForeignKey, Integer, TIMESTAMP, VARCHAR

from main import db
from models.enums import wishlist_status_to_id
# To make sure these strings get translated
from models.events_model import ShufflingEvent
from models.users_model import User

unclaimed = _("Unclaimed")
reserved = _("Reserved")
purchased = _("Purchased")
modified = _("Modified")
archived = _("Archived")


class Wishlist(db.Model):
    """
    Specifies how wishlist items are held in the database

    @param user_id: user's ID
    @param item: content of the wishlist item
    @param status: status of the item
    @param purchased_by: item has been claimed by whom
    """
    __tablename__ = "wishlists"

    id: int = Column(BigInteger, server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    user_id: int = Column(Integer, ForeignKey(User.id), nullable=False)
    item: str = Column(VARCHAR(1024), nullable=False)
    status: int = Column(Integer, ForeignKey("wishlist_status_types.id"), default=wishlist_status_to_id["default"],
                         nullable=False)
    purchased_by: int = Column(Integer, ForeignKey(User.id), nullable=True)
    event_id: int = Column(Integer, ForeignKey(ShufflingEvent.id), nullable=False)
    when: datetime = Column(TIMESTAMP, default=datetime.now(), nullable=False)

    def __init__(self,
                 user_id: int,
                 item: str,
                 status: int = wishlist_status_to_id["default"],
                 purchased_by: int = None):
        self.user_id = user_id
        self.item = item
        self.status = status
        self.purchased_by = purchased_by

    def __repr__(self):
        return "<Wishlist {}>".format(self.id)


class ArchivedWishlist(db.Model):
    """
    Specifies how deleted wishlist items are held in the database

    @param user_id: user's ID
    @param item: content of the wishlist item
    @param status: status of the item
    @param purchased_by: item has been claimed by whom
    """
    __tablename__ = "archived_wishlists"

    id: int = Column(BigInteger, server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    user_id: int = Column(Integer, ForeignKey(User.id), nullable=False)
    item: str = Column(VARCHAR(1024), nullable=False)
    status: int = Column(Integer,
                         ForeignKey("wishlist_status_types.id"),
                         default=wishlist_status_to_id["purchased"],
                         nullable=False)
    purchased_by: int = Column(Integer, ForeignKey(User.id), nullable=True)
    event_id: int = Column(Integer, ForeignKey(ShufflingEvent.id), nullable=False)
    when: datetime = Column(TIMESTAMP, server_default=FetchedValue(), nullable=False)

    def __init__(self, user_id: int,
                 item: str,
                 status: int = wishlist_status_to_id["default"],
                 purchased_by: int = None):
        self.user_id = user_id
        self.item = item
        self.status = status
        self.purchased_by = purchased_by

    def __repr__(self):
        return "<Wishlist {}>".format(self.id)
