from config import db


class UGARelationship(db.Model):
    """
    Specifies how user-group-admin relationships are modeled in the database

    @type  user_id: int
    @param user_id: user's ID
    @type  group_id: int
    @param group_id: family_id where the family belongs ID
    @type  admin: bool
    @param admin: if the user is the adming of the group
    """

    __tablename__ = "users_groups_admins"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True, unique=True, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)

    def __init__(self, user_id, group_id, admin):
        self.user_id = user_id
        self.group_id = group_id
        self.admin = admin

    def __repr__(self):
        return "<user_id {}>".format(self.user_id)
