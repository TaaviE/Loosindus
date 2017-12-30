# coding=utf-8


class Config(object):
    """DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = True

    SECRET_KEY =
    SQLALCHEMY_DATABASE_URI =
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER =
    MAIL_PORT =
    MAIL_USE_SSL =
    MAIL_USERNAME =
    MAIL_PASSWORD =
    MAIL_DEFAULT_SENDER =
    MAIL_SUPPRESS_SEND = False

    RECAPTCHA_PUBLIC_KEY =
    RECAPTCHA_PRIVATE_KEY =

    SECURITY_EMAIL_SENDER =
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT =
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_CHANGEABLE = True
"""

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = True


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


import os

from flask import Flask
from flask_mail import Mail
from flask_security import Security, SQLAlchemyUserDatastore, forms
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import RecaptchaField

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
db = SQLAlchemy(app)
mail = Mail(app)

# Setup Flask-Security
userroles = db.Table(
    "roles_users",
    db.Column("id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id"))
)

from models import users_model

user_datastore = SQLAlchemyUserDatastore(db,
                                         users_model.User,
                                         users_model.Role)


class RegistrationForm(forms.RegisterForm):
    username = forms.StringField("Eesnimi", [forms.Required()])
    recaptcha = RecaptchaField("Captcha", [forms.Required()])


security = Security(app, user_datastore, confirm_register_form=RegistrationForm)
