from datetime import datetime

from main import db
from models.groups_model import Group
from models.users_model import User


class Shuffle(db.Model):
    __tablename__ = "shuffles"

    id = db.Column(db.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    giver = db.Column(db.Integer(), db.ForeignKey(User.id), nullable=False)
    getter = db.Column(db.Integer(), db.ForeignKey(User.id), nullable=False)
    year = db.Column(db.Integer(), default=datetime.now().year, nullable=False)
    group = db.Column(db.Integer(), db.ForeignKey(Group.id))

    def __str__(self):
        return "F: " + self.giver + ", T: " + self.getter

    def __hash__(self):
        return hash(self.giver + self.getter)
