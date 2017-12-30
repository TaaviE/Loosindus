from config import db


class Family(db.Model):
    """
    Specifies how families are modeled in the database

    @type  family_id: int
    @param family_id: family's ID
    @type  family_group: int
    @param family_group: group where the family belongs ID
    @type  family_name: str
    @param family_name: 255 letter name of the group
    """

    __tablename__ = "families"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    group = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, family_id, family_group, family_name):
        self.id = family_id
        self.group = family_group
        self.name = family_name

    def __repr__(self):
        return "<id {}>".format(self.id)
