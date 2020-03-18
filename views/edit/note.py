# coding=utf-8
"""
Routes to edit comments
"""
from datetime import datetime
from logging import getLogger

import sentry_sdk
from flask import redirect, render_template, request, url_for
from flask_babelex import gettext as _
from flask_login import login_required

from config import Config
from main import db
from models.enums import wishlist_status_to_id
from models.users_model import User
from models.wishlist_model import Wishlist
from utility_standalone import get_user_id
from views.edit.blueprint import edit_page

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()


@edit_page.route("/note/<request_id>", methods=["GET"])
@login_required
def note_edit_get(request_id: str):
    """
    Displays a page where a person can edit a note
    """
    user_id = get_user_id()
    user: User = User.query.get(user_id)
    username = user.first_name
    try:
        request_id = int(request_id)
        logger.info("{} is trying to remove a note {}".format(user_id, request_id))
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_("Pls no hax ") + username + "!!",
                               title=_("Error"))

    try:
        logger.info("{} is editing notes of {}".format(user_id, request_id))
        db_note = Wishlist.query.get(request_id)
    except Exception as e:
        logger.error(e)
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_("An error occured"),
                               title=_("Error"))

    if (db_note.when - datetime.now()).days > 90:
        return render_template("utility/error.html",
                               message=_("Time to change your wishes is over, ") + username + "!!",
                               title=_("Warning"))

    return render_template("creatething.html",
                           action="ADD",
                           confirm=False,
                           endpoint=url_for("edit_page.note_edit", request_id=request_id),
                           row_count=3,
                           extra_data=request_id,
                           label=_("Your wish"),
                           placeholder=db_note.item)


@edit_page.route("/note/<request_id>", methods=["POST"])
@login_required
def note_edit(request_id: str):
    """
    Allows submitting textual edits to notes
    """
    user_id = get_user_id()
    logger.debug("Got a post request to edit a note by user id: {}".format(user_id))

    addednote = request.form["textfield"]
    try:
        request_id = int(request_id)
    except Exception as e:
        logger.error("Error when decrypting note edit submission")
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_("An error occured"),
                               title=_("Error"))

    db_note = Wishlist.query.get(request_id)

    try:
        db_note.item = addednote
        db_note.status = wishlist_status_to_id["modified"]
        db.session.commit()
    except Exception as e:
        logger.error("Error when committing note edit change into database")
        sentry_sdk.capture_exception(e)
        db.session.rollback()
        return render_template("utility/error.html",
                               message=_("An error occured"),
                               title=_("Error"))

    return render_template("utility/success.html",
                           action=_("Changed"),
                           link="/notes",
                           title=_("Changed"))


@edit_page.route("/note/remove/<request_id>", methods=["POST"])
@login_required
def note_remove(request_id: str):
    """
    Allows deleting a specific note
    """
    user_id = get_user_id()
    user = User.query.get(user_id)
    username = user.first_name

    if "confirm" not in request.form.keys():
        return render_template("creatething.html",
                               action="DELETE",
                               endpoint=url_for("edit_page.note_remove", request_id=request_id),
                               extra_data=request_id,
                               confirm=True)

    try:
        request_id = int(request_id)
        logger.info("{} is trying to remove a note {}".format(user_id, request_id))
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_("Broken link"),
                               title=_("Error"))

    try:  # Let's try to delete it now
        Wishlist.query.filter_by(id=request_id).delete()
        db.session.commit()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_(
                                   "Can't find what you wanted to delete or some other error occured while deleting"),
                               title=_("Error"))

    logger.info("Removed {} note with ID {}".format(username, request_id))
    return render_template("utility/success.html",
                           action=_("Removed"),
                           link="/notes",
                           title=_("Removed"))


@edit_page.route("/note/<id>/status", methods=["POST"])
@login_required
def update_note_status(id: str):
    """
    Allows setting specific wishlist note's status
    """
    user_id = get_user_id()

    # TODO: Check if they should be able to change?
    try:
        requested_status = int(request.form["status"])
        note = Wishlist.query.get(id)

        if requested_status != wishlist_status_to_id["default"]:
            # If the requested state is not default
            # If it's already been purchased or someone tries to set it to modified
            # then abort (modified only happens after edit of a note)
            if note.status == wishlist_status_to_id["purchased"] or \
                    requested_status == wishlist_status_to_id["modified"]:
                raise Exception("Invalid access")
            note.status = requested_status
            note.purchased_by = user_id
            db.session.commit()
        elif requested_status == wishlist_status_to_id["default"]:
            # If the request is to set it to default
            # If the note has already been purchased or someone tried to set it to modified
            # then abort (modified state should only happens after edit of a note)
            if note.status == wishlist_status_to_id["purchased"] or \
                    requested_status == wishlist_status_to_id["modified"]:
                raise Exception("Invalid access")
            note.status = requested_status
            note.purchased_by = None
            db.session.commit()
        else:
            raise Exception("Invalid status code")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.info("Failed toggling: {}".format(e))
        return render_template("utility/error.html",
                               message=_("Could not edit"),
                               title=_("Error"),
                               back=True)

    return redirect(url_for("main_page.wishlist", person_id=note.user_id), code=303)
