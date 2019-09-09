# coding=utf-8
from datetime import datetime

from flask_babelex import gettext as _
from sqlalchemy import BigInteger, Column, FetchedValue, ForeignKey, Integer, TIMESTAMP, VARCHAR

from main import db
# To make sure these strings get translated
from models.events_model import ShufflingEvent
from models.users_model import User

unclaimed = _("Unclaimed")
reserved = _("Reserved")
purchased = _("Purchased")
modified = _("Modified")
archived = _("Archived")


class WishlistStatusType(db.Model):
    """
    Specifies the different states a note can be in
    """
    __tablename__ = "wishlist_status_types"
    id: int = Column(Integer, server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    name: str = Column(VARCHAR(255), nullable=False)


wishlist_status_to_id = {}
for status in WishlistStatusType.query.all():
    wishlist_status_to_id[status.name.lower().replace(" ", "_")] = status.id


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
    status: int = Column(Integer, ForeignKey(WishlistStatusType.id), default=wishlist_status_to_id["default"],
                         nullable=False)
    purchased_by: int = Column(Integer, ForeignKey(User.id), nullable=True)
    event_id: int = Column(Integer, ForeignKey(ShufflingEvent.id), nullable=False)

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
    status: int = Column(Integer, ForeignKey(WishlistStatusType.id), default=wishlist_status_to_id["purchased"],
                         nullable=False)
    purchased_by: int = Column(Integer, ForeignKey(User.id), nullable=True)
    event_id: int = Column(Integer, ForeignKey(ShufflingEvent.id), nullable=False)
    archived: datetime = Column(TIMESTAMP, nullable=False)

    def __init__(self, user_id: int, item: str, status: int = wishlist_status_to_id["default"],
                 purchased_by: int = None):
        self.user_id = user_id
        self.item = item
        self.status = status
        self.purchased_by = purchased_by

    def __repr__(self):
        return "<Wishlist {}>".format(self.id)
