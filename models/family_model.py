from main import db


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


class FamilyGroup(db.Model):
    """
    Specifies how family-group relationships are defined in the database

    @type  family_id: int
    @param family_id: family's ID
    @type  group_id: int
    @param group_id: ID of the group where the family belongs
    """

    __tablename__ = "families_groups"
    family_id = db.Column(db.Integer, primary_key=True, unique=False, nullable=False)
    group_id = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, family_id, family_group):
        self.family_id = family_id
        self.group_id = family_group

    def __repr__(self):
        return "<id {}>".format(self.family_id)
