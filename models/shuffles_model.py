from config import db


class Shuffle(db.Model):
    __tablename__ = "shuffles"
    giver = db.Column(db.Integer(), db.ForeignKey("user.id"), primary_key=True)
    getter = db.Column(db.Integer(), db.ForeignKey("user.id"))

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
