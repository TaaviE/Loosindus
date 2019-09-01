# coding=utf-8
"""
Contains everything very directly related to users
"""
from datetime import datetime

from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_security import RoleMixin, UserMixin
from sqlalchemy import Boolean, Column, DateTime, FetchedValue, ForeignKey, Integer, VARCHAR
from sqlalchemy.orm import backref, relationship

from main import db
from models.family_model import Family


class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id: int = Column(Integer(), server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    name: str = Column(VARCHAR(80), unique=True)
    description: str = Column(VARCHAR(255))

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id: int = Column(Integer, server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    email: str = Column(VARCHAR(255), unique=True)
    first_name: str = Column(VARCHAR(255), nullable=False)
    password: str = Column(VARCHAR(255), nullable=False)
    confirmed_at: datetime = Column(DateTime())
    active: bool = Column(Boolean())

    birthday: datetime = Column(DateTime())
    language: str = Column(VARCHAR(5), default="en", nullable=False)

    roles = relationship(
        Role,
        secondary="roles_users",
        backref=backref("User", lazy="dynamic")
    )

    @property
    def last_login_ip(self):
        return self.last_login_ip

    @last_login_ip.setter
    def last_login_ip(self, value):
        self.last_login_ip = value

    @property
    def last_login_at(self):
        return self.last_login_at

    @last_login_at.setter
    def last_login_at(self, value):
        self.last_login_at = value

    @property
    def current_login_at(self):
        return self.current_login_at

    @current_login_at.setter
    def current_login_at(self, value):
        self.current_login_at = value

    @property
    def current_login_ip(self):
        return self.current_login_ip

    @current_login_ip.setter
    def current_login_ip(self, value):
        self.current_login_ip = value

    def __init__(self, email, username, password, active=False):
        self.email = email
        self.username = username
        self.password = password
        self.active = active


class RolesUsers(db.Model):
    """
    Specifies what role an User has
    """
    __tablename__ = "roles_users"
    id = Column(Integer(), ForeignKey(User.id), primary_key=True)
    role_id = Column(Integer(), ForeignKey(Role.id))


class AuthLinks(db.Model, OAuthConsumerMixin):
    """
    Specifies how 3rd party identity providers are linked to users
    """
    __tablename__ = "user_connections"
    id = Column(Integer, server_default=FetchedValue(), primary_key=True, unique=True, nullable=False)
    provider_user_id = Column(VARCHAR(255), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    token = Column(VARCHAR(255), nullable=True)
    provider = Column(VARCHAR(255), nullable=False)

    def __init__(self, provider_user_id, provider, token=None, user_id=None):
        self.provider_user_id = provider_user_id
        self.user_id = user_id
        self.provider = provider
        self.token = token


class Email(db.Model):
    """
    Specifies how emails are stored for history and management purposes
    Users table is updated based on this table by a stored procedure
    """
    __tablename__ = "emails"

    email: str = Column(VARCHAR(255), primary_key=True, unique=True, nullable=False)
    verified: bool = Column(Boolean, default=False, nullable=False)
    primary: bool = Column(Boolean, default=False, nullable=False)
    user_id: int = Column(Integer, ForeignKey(User.id), nullable=False)
    added: datetime = Column(DateTime, server_default=FetchedValue(), nullable=False)


class Password(db.Model):
    """
    Specifies how passwords are stored in the database,
    Users table is updated based on this table by a stored procedure
    """
    __tablename__ = "passwords"

    password: str = Column(VARCHAR(255), primary_key=True, unique=True, nullable=False)
    user_id: int = Column(Integer, ForeignKey(User.id), nullable=False)
    active: bool = Column(Boolean, default=False, nullable=False)
    created: datetime = Column(DateTime, default=datetime.now(), nullable=False)


class UserFamilyAdmin(db.Model):
    """
    Specifies how user-family (admin) relationships are modeled in the database

    @param user_id: user's ID
    @param family_id: family_id where the family belongs ID
    @param admin: if the user is the admin of the family
    """

    __tablename__ = "users_families_admins"
    user_id: int = Column(Integer, ForeignKey(User.id), primary_key=True, nullable=False)
    family_id: int = Column(Integer, ForeignKey(Family.id), primary_key=True, nullable=False)
    admin: bool = Column(Boolean, nullable=False)
    confirmed: bool = Column(Boolean, nullable=False, default=False)

    def __init__(self, user_id, family_id, admin):
        self.user_id = user_id
        self.family_id = family_id
        self.admin = admin

    def __repr__(self):
        return "<user_id {}>".format(self.user_id)


class UserGroupAdmin(db.Model):
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
    user_id: int = Column(Integer, ForeignKey("user.id"), primary_key=True, unique=True, nullable=False)
    group_id: int = Column(Integer, ForeignKey("groups.id"), primary_key=True, nullable=False)
    admin: bool = Column(Boolean, nullable=False)
    confirmed: bool = Column(Boolean, nullable=False, default=False)

    def __init__(self, user_id: int, group_id: int, admin: bool):
        self.user_id = user_id
        self.group_id = group_id
        self.admin = admin

    def __repr__(self):
        return "<user_id {}, group_id {}>".format(self.user_id, self.group_id)
