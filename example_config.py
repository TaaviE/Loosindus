# coding=utf-8
import logging
import subprocess


class Config(object):
    ENV = "debug"  # TODO: Replace with "production"
    FLASK_DEBUG = True  # TODO: Disable in production
    DEVELOPMENT = True  # TODO: Disable in production
    DEBUG = True  # TODO: Disable in production
    TESTING = True  # TODO: Disable in production

    CSRF_ENABLED = False  # TODO: Enable in production
    WTF_CSRF_ENABLED = False  # TODO: Enable in production

    SENTRY_PUBLIC_DSN = ""  # The full DSN given without(!) the private key
    SENTRY_PUBLIC_KEY = ""  # TODO: The hash part

    CURRENT_GIT_SHA = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()

    AES_KEY = b""  # TODO: Update AES key
    SECRET_KEY = ""  # TODO: Update secret key info

    SQLALCHEMY_DATABASE_URI = ""  # TODO: Add database URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SERVER_NAME = "https://example.com"  # TODO: Fill this to make sure sitemap and robots.txt gets filled properly
    CONTACT_EMAIL = "host@example.com"  # TODO: So that people can e-mail you

    MAIL_SERVER = "localhost"
    MAIL_PORT = 25
    MAIL_USE_SSL = False
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""  # TODO: Add email server info
    MAIL_DEFAULT_SENDER = ("Pretty mailer name", "place@holder")  # TODO: Update email sender info
    MAIL_SUPPRESS_SEND = True  # TODO: Do not suppress send in production

    SHUFFLE_SEED = 0  # TODO: This is used to shuffle symbols displayed to users, keep secret to keep the surprise

    RECAPTCHA_PUBLIC_KEY = ""  # TODO: Add captcha keys
    RECAPTCHA_PRIVATE_KEY = ""

    SECURITY_EMAIL_SENDER = ("Pretty mailer name", "place@holder")  # TODO: Update email sender info
    SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
    SECURITY_PASSWORD_SALT = None  # TODO: Add salt!

    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = False

    USER_AFTER_REGISTER_ENDPOINT = "/login"

    SESSION_COOKIE_SECURE = False  # TODO: Enable in production
    REMEMBER_COOKIE_SECURE = False  # TODO: Enable in production
    SESSION_COOKIE_HTTPONLY = False  # TODO: Enable in production
    REMEMBER_COOKIE_HTTPONLY = False  # TODO: Enable in production
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SAMESITE = "Lax"

    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True

    TLS_PROXY_SECRET = "__"  # TODO: Make sure TLS-Client-Secret header value matches,
    # this is a countermeasure to forgetting to proxy

    LOGLEVEL = logging.DEBUG

    BABEL_DEFAULT_LOCALE = "ee"  # TODO: You might want to change this to "en" if you want to default to English

    CELERY_BROKER_URL = ""  # TODO: URL to your Celery broker
    CELERY_RESULT_BACKEND = ""  # TODO: URL to your Celery result backend

    OAUTHLIB_INSECURE_TRANSPORT = False
    OAUTHLIB_RELAX_TOKEN_SCOPE = True

    GOOGLE_OAUTH = False
    GOOGLE_OAUTH_CLIENT_ID = ""
    GOOGLE_OAUTH_CLIENT_SECRET = ""

    GITHUB_OAUTH = False
    GITHUB_OAUTH_CLIENT_ID = ""
    GITHUB_OAUTH_CLIENT_SECRET = ""

    FACEBOOK_OAUTH = False
    FACEBOOK_OAUTH_CLIENT_ID = ""
    FACEBOOK_OAUTH_CLIENT_SECRET = ""

    ESTEID_AUTH = False  # TODO: Requires web server configuration

    GOOGLE_ADS = False  # TODO: If you want to display unintrusive ads CONFIGURE BELOW
    DATA_AD_CLIENT = "ca-pub-asdfghjklmnopqrstuvxy"  # TODO: Update AD client field value
    DATA_AD_SLOT = "1234567890"  # TODO: Update AD slot field value

    GAUA = "UA-1234314234-2"  # TODO: Google Analytics User ID

    SQLALCHEMY_ENGINE_OPTIONS = {  # This is to make sure the service stays alive even if connections time out
        "pool_pre_ping": True,
    }
