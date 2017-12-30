from config import db


class Groups(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, id, admin):
        self.id = id
        self.admin = admin

    def __repr__(self):
        return "<id {}>".format(self.id)
