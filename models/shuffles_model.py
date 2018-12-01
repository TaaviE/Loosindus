from main import db


class Shuffle(db.Model):
    __tablename__ = "shuffles"
    giver = db.Column(db.Integer(), db.ForeignKey("user.id"), primary_key=True, nullable=False)
    getter = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)

    def __str__(self):
        return "F: " + self.giver + ", T: " + self.getter

    def __hash__(self):
        return hash(self.giver + self.getter)
