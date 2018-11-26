from enum import Enum

from django.contrib.auth.models import User

from django.db.models import Model, ForeignKey, CASCADE, IntegerField, CharField


class NoteState(Enum):
    """
    Describes all the possible states of a wishlist item
    """
    DEFAULT = {"id": -1, "description": "Vaba", "color": "#4CAF50"}
    """Default state"""
    PLANNING_TO_PURCHASE = {"id": 0, "description": "Reserveeri(tud)", "color": "#FFEB3B"}
    """Plans to purchase"""
    PURCHASED = {"id": 2, "description": "Ostetud", "color": "#F44336"}
    """Purchased"""
    MODIFIED = {"id": 3, "description": "Muudetud", "color": "#4CAF50"}
    """Modified"""


class Wishlist(Model):
    """
    Specifies how wishlist items are held in the database

    @type  id: int
    @param id: note's ID
    @type  user_id: int
    @param user_id: user's ID
    @type  item: str
    @param item: content of the wishlist item
    @type  status: NoteState
    @param status: status of the item
    @type  purchased_by: int
    @param purchased_by: item has been claimed by whom
    """

    class Meta:
        db_table = "wishlists"

    id = IntegerField(primary_key=True, null=False, blank=True)
    user_id = IntegerField(ForeignKey(User, db_column='id', on_delete=CASCADE), null=False, blank=True)
    item = CharField(max_length=1024, null=False, blank=True)
    status = IntegerField(null=False, blank=True)
    purchased_by = IntegerField(ForeignKey(User, db_column='id', on_delete=CASCADE), null=True, blank=False)
