# coding=utf-8
# Copyright: Taavi Eomäe 2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Routes for editing user accounts
"""
import sentry_sdk
from flask import render_template, request
from flask_babelex import gettext as _
from flask_login import login_required

from main import db
from models.users_model import User
from utility_standalone import get_user_id
from views.edit.blueprint import edit_page


@edit_page.route("/language", methods=["POST"])
@login_required
def set_language():
    """
    Allows the user to set their language
    """
    user_id = get_user_id()

    try:
        if request.form["language"] in ["en", "ee"]:
            user = User.query.filter(User.id == user_id).first()
            try:
                user.language = request.form["language"]
                db.session.commit()
            except Exception as e:
                sentry_sdk.capture_exception(e)
                db.session.rollback()
                return render_template("utility/error.html",
                                       message=_("Faulty input"),
                                       title=_("Error"))

        return render_template("utility/success.html",
                               action=_("Added"),
                               link="/notes",
                               title=_("Added"))
    except Exception:
        # No need to capture with Sentry, someone's just meddling
        return render_template("utility/error.html",
                               message=_("Faulty input"),
                               title=_("Error"))
