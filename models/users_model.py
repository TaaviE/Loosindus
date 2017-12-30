from flask_security import UserMixin, RoleMixin
from sqlalchemy.dialects.postgresql import ARRAY

from config import db


class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship(
        "Role",
        secondary="roles_users",
        backref=db.backref("User", lazy="dynamic")
    )
    family_id = db.Column(db.Integer, db.ForeignKey("families.id"))
    admin_of_groups = db.Column(ARRAY(db.Integer))
    admin_of_families = db.Column(ARRAY(db.Integer))
