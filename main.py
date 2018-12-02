import os

from flask import Flask

from config import Config

if Config.DEBUG:
    from flask_babel import Babel
else:
    from flask_babelex import Babel
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from forms import ExtendedConfirmationForm, ExtendedForgotPasswordForm, ExtendedRegisterForm, ExtendedResetForm

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)
db = SQLAlchemy(app)
babel = Babel(app)

from raven.contrib.flask import Sentry

if not Config.DEBUG:
    sentry = Sentry(app, dsn=Config.SENTRY_URL, logging=False)
else:
    sentry = Sentry(app, dsn=None, logging=False)

from models.users_model import User, Role
from flask_security import SQLAlchemyUserDatastore, Security

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore,
                    confirm_register_form=ExtendedRegisterForm,
                    reset_password_form=ExtendedResetForm,
                    send_confirmation_form=ExtendedConfirmationForm,
                    forgot_password_form=ExtendedForgotPasswordForm)

from views import main_page

app.register_blueprint(main_page)
