from sqlalchemy.dialects.postgresql import JSON

from config import db


class Notes(db.Model):
    __tablename__ = "wishlist"

    user_id = db.Column(db.Integer, primary_key=True)
    notes = db.Column(JSON)
    notes_purchased = db.Column(JSON)

    def __init__(self, notes, user_id, notes_purchased):
        self.user_id = user_id
        self.notes = notes
        self.notes_purchased = notes_purchased

    def __repr__(self):
        return "<id {}>".format(self.id)
