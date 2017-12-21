import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG =
    TESTING =
    CSRF_ENABLED = True
    SECRET_KEY =
    SQLALCHEMY_DATABASE_URI =
    MAIL_SERVER =
    MAIL_PORT =
    MAIL_USE_SSL =
    MAIL_USERNAME =
    MAIL_PASSWORD =
    SECURITY_PASSWORD_HASH =
    SECURITY_PASSWORD_SALT =
    SECURITY_REGISTERABLE =


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
