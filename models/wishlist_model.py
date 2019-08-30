# coding=utf-8
from datetime import datetime
from enum import Enum

from flask_babelex import gettext as _
from sqlalchemy import VARCHAR, Integer, Column, TIMESTAMP, BigInteger, ForeignKey

from main import db
# To make sure these strings get translated
from models.events_model import ShufflingEvent
from models.users_model import User

unclaimed = _("Unclaimed")
reserved = _("Reserved")
purchased = _("Purchased")
modified = _("Modified")
archived = _("Archived")


class NoteState(Enum):
    """
    Describes all the possible states of a wishlist item
    """
    DEFAULT = {"id": -1, "description": _("Unclaimed"), "color": "#4CAF50"}
    """Default state"""
    PLANNING_TO_PURCHASE = {"id": 0, "description": _("Reserved"), "color": "#FFEB3B"}
    """Plans to purchase"""
    PURCHASED = {"id": 2, "description": _("Purchased"), "color": "#F44336"}
    """Purchased"""
    MODIFIED = {"id": 3, "description": _("Modified"), "color": "#4CAF50"}
    """Modified"""


class Wishlist(db.Model):
    """
    Specifies how wishlist items are held in the database

    @param user_id: user's ID
    @param item: content of the wishlist item
    @param status: status of the item
    @param purchased_by: item has been claimed by whom
    """
    __tablename__ = "wishlists"

    user_id: int = Column(Integer)
    item: str = Column(VARCHAR(1024))
    status: int = Column(Integer, default=NoteState.DEFAULT.value["id"], nullable=False)
    purchased_by: int = Column(Integer, nullable=True)
    received: datetime = Column(TIMESTAMP, nullable=True)
    event_id: int = Column(Integer, ForeignKey(ShufflingEvent.id), nullable=False)
    id: int = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)

    def __init__(self, user_id: int, item: str, status: int = NoteState.DEFAULT.value["id"], purchased_by: int = None):
        self.user_id = user_id
        self.item = item
        self.status = status
        self.purchased_by = purchased_by

    def __repr__(self):
        return "<id {}>".format(self.user_id)


class ArchivedWishlist(db.Model):
    """
    Specifies how deleted wishlist items are held in the database

    @param user_id: user's ID
    @param item: content of the wishlist item
    @param status: status of the item
    @param purchased_by: item has been claimed by whom
    """
    __tablename__ = "archived_wishlists"

    id: int = Column(BigInteger, primary_key=True, autoincrement=False, nullable=False)
    item: str = Column(VARCHAR(1024))
    status: int = Column(Integer, default=NoteState.DEFAULT.value["id"], nullable=False)
    purchased_by: int = Column(Integer, ForeignKey(User.id), nullable=True)
    user_id: int = Column(Integer, ForeignKey(User.id))
    event_id: int = Column(Integer, ForeignKey(ShufflingEvent.id), nullable=False)
    archived: datetime = Column(TIMESTAMP, nullable=False)

    def __init__(self, user_id: int, item: str, status: int = NoteState.DEFAULT.value["id"], purchased_by: int = None):
        self.user_id = user_id
        self.item = item
        self.status = status
        self.purchased_by = purchased_by

    def __repr__(self):
        return "<id {}>".format(self.user_id)
