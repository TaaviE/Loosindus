from flask_security import UserMixin, RoleMixin
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import backref, relationship

from main import db


class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id = Column(Integer(), primary_key=True, unique=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class RolesUsers(db.Model):
    __tablename__ = "roles_users"
    id = Column("id", Integer(), ForeignKey("user.id"), primary_key=True)
    role_id = Column("role_id", Integer(), ForeignKey("role.id"))


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    email = Column(String(255), unique=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(255))
    last_activity_at = Column(DateTime())
    last_activity_ip = Column(String(255))
    current_login_ip = Column(String(255))
    language = Column(String(5))
    login_count = Column(Integer)
    roles = relationship(
        "Role",
        secondary=RolesUsers.__tablename__,
        backref=backref("User", lazy="dynamic")
    )


from flask_dance.consumer.backend.sqla import OAuthConsumerMixin


class Links(db.Model, OAuthConsumerMixin):
    __tablename__ = "user_connection"
    provider_user_id = Column(String(255), unique=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User)

    def __init__(self, provider_user_id, user_id, provider):
        self.provider_user_id = provider_user_id
        self.user_id = user_id
        self.provider = provider
