from main import db


class SubscriptionType(db.Model):
    __tablename__ = "subscription_types"

    id = db.Column(db.Integer(255), primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.VARCHAR(255), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<id {}>".format(self.id)
