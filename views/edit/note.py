# coding=utf-8
# Copyright: Taavi Eomäe 2018-2020
# SPDX-License-Identifier: AGPL-3.0-only
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
from models.wishlist_model import ArchivedWishlist, Wishlist
from utility_standalone import get_user_id
from views.edit.blueprint import edit_page

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()


@edit_page.route("/note/add", methods=["GET"])
@login_required
def note_add():
    """
    :return: Displays the form required to add a note
    """
    return render_template("creatething.html",
                           action="ADD",
                           confirm=False,
                           endpoint=url_for("edit_page.note_add_post"),
                           row_count=3,
                           label=_("Your wish"),
                           placeholder="")


@edit_page.route("/note/add", methods=["POST"])
@login_required
def note_add_post():
    """
    Allows submitting new notes to a wishlist
    """
    logger.debug("Got a post request to add a note")
    user_id = get_user_id()
    user: User = User.query.get(user_id)
    username = user.first_name
    logger.debug(f"Found user: {username} with id: {user_id}")
    currentnotes = {}
    if "textfield" not in request.form.keys():
        return render_template("utility/error.html",
                               message=_("Error, no form content"),
                               title=_("Error"))

    addednote = request.form["textfield"]

    if len(addednote) > 1024:
        return render_template("utility/error.html",
                               message=_("You're wishing for too much"),
                               title=_("Error"))
    elif len(addednote) <= 0:
        return render_template("utility/error.html",
                               message=_("Santa can't bring you nothing, ") + username + "!",
                               title=_("Error"))

    logger.debug(f"Trying to add a note: {addednote}")
    try:
        logger.info(f"Opening file: {user_id}")
        db_notes = Wishlist.query.filter(Wishlist.user_id == user_id).all()
        for note in db_notes:
            currentnotes[note.item] = note.id
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise e

    if len(currentnotes) >= 200:
        logger.info(f"User {user_id} wanted to add too many notes")
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
        logger.error(f"User {user_id} caused an error adding a note to database")
        sentry_sdk.capture_exception(e)
        raise e

    logger.info(f"User {user_id} successfully added a note to database")
    return render_template("utility/success.html",
                           action=_("Added"),
                           link="/notes",
                           title=_("Added"))


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
        logger.info(f"{user_id} is trying to remove a note {request_id}")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_("Pls no hax ") + username + "!!",
                               title=_("Error"))

    try:
        logger.info(f"{user_id} is editing notes of {request_id}")
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
    logger.debug("Got a post request to edit a note by user id: {user_id}")

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
        logger.info(f"{user_id} is trying to remove a note {request_id}")
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
        logger.error(e)
        return render_template("utility/error.html",
                               message=_(
                                   "Can't find what you wanted to delete or some other error occured while deleting"),
                               title=_("Error"))

    logger.info(f"Removed {username} note with ID {request_id}")
    return render_template("utility/success.html",
                           action=_("Removed"),
                           link=url_for("main_page.notes"),
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
        logger.info(f"Failed toggling: {e}")
        return render_template("utility/error.html",
                               message=_("Could not edit"),
                               title=_("Error"),
                               back=True)

    return redirect(url_for("main_page.wishlist", person_id=note.user_id), code=303)


@edit_page.route("/note/restore/<note_id>", methods=["GET"])
@login_required
def note_restore(note_id: str):
    """
    @param note_id: The archived note to restore and place into the wishlist
    """
    user_id = get_user_id()
    note_id = int(note_id)

    note: ArchivedWishlist = ArchivedWishlist.query.get(note_id)
    if note.user_id != user_id:
        return render_template("utility/error.html",
                               message=_("Could not restore"),
                               title=_("Error"),
                               back=True)

    db_entry_notes = Wishlist(
        user_id=note.user_id,
        item=note.item
    )

    try:
        db.session.add(db_entry_notes)
        db.session.commit()
    except Exception as e:
        logger.debug(f"User {user_id} caused an error \"{e}\" restoring a note")
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_("Could not restore"),
                               title=_("Error"),
                               back=True)

    return render_template("utility/success.html",
                           action=_("Restored"),
                           link=url_for("main_page.notes"),
                           title=_("Restored"))
