from datetime import datetime

from main import db
from models.groups_model import Group
from models.users_model import User


class Shuffle(db.Model):
    __tablename__ = "shuffles"
    giver = db.Column(db.Integer(), db.ForeignKey(User.id), primary_key=True, nullable=False)
    getter = db.Column(db.Integer(), db.ForeignKey(User.id), nullable=False)
    year = db.Column(db.DateTime(), nullable=False, default=datetime.now())
    group = db.Column(db.Integer(), db.ForeignKey(Group.id))

    def __str__(self):
        return "F: " + self.giver + ", T: " + self.getter

    def __hash__(self):
        return hash(self.giver + self.getter)
