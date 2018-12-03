import os

from celery import Celery
from flask import Flask
from flask_babelex import Babel
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from config import Config
from forms import ExtendedConfirmationForm, ExtendedForgotPasswordForm, ExtendedRegisterForm, ExtendedResetForm

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)
db = SQLAlchemy(app)
babel = Babel(app)
celery = Celery()
celery.conf.update(app.config)

from raven.contrib.flask import Sentry

if not Config.DEBUG:
    sentry = Sentry(app, dsn=Config.SENTRY_URL, logging=False)
else:
    sentry = Sentry(app, dsn=None, logging=False)

from models.users_model import User, Role, AuthLinks
from flask_security import SQLAlchemyUserDatastore, Security

user_datastore = SQLAlchemyUserDatastore(db, User, Role)

security = Security(app, user_datastore,
                    confirm_register_form=ExtendedRegisterForm,
                    reset_password_form=ExtendedResetForm,
                    send_confirmation_form=ExtendedConfirmationForm,
                    forgot_password_form=ExtendedForgotPasswordForm)

from views import main_page

app.register_blueprint(main_page)

from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend

google_blueprint = make_google_blueprint(
    scope=[
        "https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
    client_id=Config.GOOGLE_OAUTH_CLIENT_ID,
    client_secret=Config.GOOGLE_OAUTH_CLIENT_SECRET,
)

from flask_login import current_user

google_blueprint.backend = SQLAlchemyBackend(AuthLinks, db.session, user=current_user)
app.register_blueprint(google_blueprint, url_prefix="/login")
