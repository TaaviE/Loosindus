# coding=utf-8
"""
Routes to edit events
"""
from flask import render_template, request
from flask_babelex import gettext as _
from flask_login import login_required

from utility_standalone import get_user_id
from views.edit.blueprint import edit_page


@edit_page.route("/event/<event_id>/graph/regenerate", methods=["GET"])
@login_required
def ask_regraph(event_id: str):
    """
    Displays a confirmation page before reshuffling
    """
    if "extra_data" in request.form.keys():
        extra_data = request.form["extra_data"]
        return render_template("creatething.html",
                               action="ADD",
                               endpoint="recreategraph",
                               extra_data=extra_data,
                               confirm=True)
    else:
        return render_template("utility/error.html",
                               message=_("An error has occured"),
                               title=_("Error"))


@edit_page.route("/event/<event_id>/graph/regenerate", methods=["POST"])
@login_required
def regraph(event_id: str):
    user_id = get_user_id()
    event_id = int(event_id)
    # TODO: Celery task invoke

    return render_template("utility/success.html",
                           action=_("Added to queue"),
                           link="/notes",
                           title=_("Shuffling started"))


@edit_page.route("/event/<id>", methods=["GET"])
@login_required
def modify_event(id: str):
    return ""


@edit_page.route("/event/<id>", methods=["POST"])
@login_required
def modify_event_with_action(id: str):
    return ""
