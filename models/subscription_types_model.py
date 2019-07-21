from sqlalchemy import FetchedValue

from main import db


class SubscriptionType(db.Model):
    """
    Specifies different types of subscriptions
    """
    __tablename__ = "subscription_types"

    id = db.Column(db.Integer(), db.Sequence("subscription_types_id_seq", start=1, increment=1),
                   server_default=FetchedValue(), primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.VARCHAR(255), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<id {}>".format(self.user_id)

    def __str__(self):
        return "{\"id\": {id}, \"name\": \"{name}\"}".format(id=self.id, name=self.name)
