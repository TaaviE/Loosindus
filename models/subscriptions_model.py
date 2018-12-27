from main import db
from models.users_model import User


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    until = db.Column(db.TIMESTAMP, nullable=False)

    def __init__(self, user_id, type, until):
        self.user_id = user_id
        self.type = type
        self.until = until

    def __repr__(self):
        return "<id {}>".format(self.user_id)
