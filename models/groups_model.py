from main import db


class Groups(db.Model):
    """
    Specifies how groups are modeled in the database

    @type  group_id: int
    @param group_id: group's ID
    @type  group_name: str
    @param group_name: 255 letter name of the group
    """
    __tablename__ = "groups"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.VARCHAR(255), nullable=True)
    description = db.Column(db.VARCHAR(255), nullable=True)

    def __init__(self, group_id, group_name):
        self.id = group_id
        self.name = group_name

    def __repr__(self):
        return "<id {}>".format(self.id)
