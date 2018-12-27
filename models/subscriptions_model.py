from sqlalchemy.sql.schema import ForeignKey, Column
from sqlalchemy.sql.sqltypes import Integer, TIMESTAMP

from main import db
from models.users_model import User


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    user_id = Column(Integer, ForeignKey(User.id), primary_key=True, nullable=False)
    type = Column(Integer, nullable=False)
    until = Column(TIMESTAMP, nullable=False)

    def __init__(self, user_id, type, until):
        self.user_id = user_id
        self.type = type
        self.until = until

    def __repr__(self):
        return "<id {}>".format(self.user_id)
