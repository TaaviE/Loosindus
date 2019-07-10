# coding=utf-8
# Copyright: Taavi Eomäe 2017-2019
# SPDX-License-Identifier: AGPL-3.0-only
"""
A simple Secret Santa website in Python
Copyright (C) 2017-2019 Taavi Eomäe

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
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
celery = Celery(app.import_name,
                backend=Config.CELERY_RESULT_BACKEND,
                broker=Config.CELERY_BROKER_URL)
celery.conf.update(app.config)

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
