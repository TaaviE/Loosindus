from config import db


class Name(db.Model):
    __tablename__ = "names_genitive"

    name = db.Column(db.VARCHAR(255), primary_key=True, nullable=False)
    genitive = db.Column(db.VARCHAR(255), nullable=False)

    def __init__(self, name, genitive):
        self.name = name
        self.genitive = genitive

    def __repr__(self):
        return "<id {}>".format(self.id)
