from config import db


class Family(db.Model):
    __tablename__ = "families"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    group = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
