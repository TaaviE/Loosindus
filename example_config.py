# coding=utf-8
from celery import Celery


class Config(object):
    """DEVELOPMENT =
    DEBUG =
    TESTING = """

    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = True

    SECRET_KEY = ""
    SQLALCHEMY_DATABASE_URI = "postgresql://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = ""
    MAIL_PORT = 25
    MAIL_USE_SSL = False
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = ""
    MAIL_SUPPRESS_SEND = False

    RECAPTCHA_PUBLIC_KEY = ""
    RECAPTCHA_PRIVATE_KEY = ""

    SECURITY_EMAIL_SENDER = ""
    SECURITY_PASSWORD_HASH = ""
    SECURITY_PASSWORD_SALT = ""
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_CHANGEABLE = True


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
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
from werkzeug.contrib.fixers import ProxyFix

ProxyFix(app, num_proxies=1)
db = SQLAlchemy(app)
mail = Mail(app)
celery = Celery()
