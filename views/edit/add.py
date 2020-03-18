# coding=utf-8
"""
Routes to create new things
"""
from logging import getLogger

import sentry_sdk
from flask import render_template, request, url_for
from flask_babelex import gettext as _
from flask_login import login_required

from config import Config
from main import db
from models.users_model import User
from models.wishlist_model import Wishlist
from utility_standalone import get_user_id
from views.edit.blueprint import edit_page

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()


@edit_page.route("/note/add", methods=["GET"])
@login_required
def createnote():
    """
    :return: Displays the form required to add a note
    """
    return render_template("creatething.html",
                           action="ADD",
                           confirm=False,
                           endpoint=url_for("edit_page.note_add_new"),
                           row_count=3,
                           label=_("Your wish"),
                           placeholder="")


@edit_page.route("/note/add", methods=["POST"])
@login_required
def note_add_new():
    """
    Allows submitting new notes to a wishlist
    """
    logger.debug("Got a post request to add a note")
    user_id = get_user_id()
    user: User = User.query.get(user_id)
    username = user.first_name
    logger.debug("Found user: {username} with id: {id}".format(username=username, id=user_id))
    currentnotes = {}
    addednote = request.form["textfield"]

    if len(addednote) > 1024:
        return render_template("utility/error.html",
                               message=_("You're wishing for too much"),
                               title=_("Error"))
    elif len(addednote) <= 0:
        return render_template("utility/error.html",
                               message=_("Santa can't bring you nothing, ") + username + "!",
                               title=_("Error"))

    logger.info("Trying to add a note: {}".format(addednote))
    try:
        logger.info("Opening file: {}".format(user_id))
        db_notes = Wishlist.query.filter(Wishlist.user_id == user_id).all()
        for note in db_notes:
            currentnotes[note.item] = note.id
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise e

    if len(currentnotes) >= 200:
        logger.info("User {user_id} wanted to add too many notes".format(user_id=user_id))
        return render_template("utility/error.html",
                               message=_("You're wishing for too much, ") + username + ".",
                               title=_("Error"))

    db_entry_notes = Wishlist(
        user_id=user_id,
        item=addednote
    )

    try:
        db.session.add(db_entry_notes)
        db.session.commit()
    except Exception as e:
        logger.error("User {user_id} caused an error adding a note to database".format(user_id=user_id))
        sentry_sdk.capture_exception(e)
        raise e

    logger.info("User {user_id} successfully added a note to database".format(user_id=user_id))
    return render_template("utility/success.html",
                           action=_("Added"),
                           link="/notes",
                           title=_("Added"))


@edit_page.route("/family/add", methods=["GET"])
@login_required
def add_family():
    return render_template("creatething.html",
                           row_count=1,
                           endpoint="editfam",
                           label=_("Group ID"))


@edit_page.route("/group/add", methods=["GET"])
@login_required
def add_group():
    """
    Allows creating a single empty group with the given name
    """
    return render_template("creatething.html",
                           row_count=1,
                           endpoint="editgroup",
                           label=_("Group ID"))
