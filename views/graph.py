# coding=utf-8
# Copyright: Taavi Eomäe 2017-2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Contains all of the routes that deal with displaying graphs
"""
from json import dumps
from logging import getLogger

import sentry_sdk
from flask import Blueprint, render_template, request
from flask_babelex import gettext as _
from flask_security import login_required
from sqlalchemy import and_

from config import Config
from models.shuffles_model import Shuffle
from utility_standalone import get_christmasy_emoji, get_user_id

graph_page = Blueprint("graph_page",
                       __name__,
                       template_folder="templates")

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()


@graph_page.route("/graph")
@login_required
def graph():
    """
    Display default group's graph
    """
    user_id = get_user_id()
    try:
        if "group_id" in request.args.keys():
            family_group = request.args["group_id"]
        else:
            family = get_default_family(user_id)
            family_group = FamilyGroup.query.filter(and_(FamilyGroup.family_id == family.id,
                                                         FamilyGroup.confirmed == True)
                                                    ).one().group_id

        if "unhide" in request.args.keys():  # TODO: Make prettier
            if request.args["unhide"] in "True":
                unhide = "True"
                user_number = _("or with your own name")
            else:
                unhide = ""
                user_number = get_christmasy_emoji(user_id)
        else:
            unhide = ""
            user_number = get_christmasy_emoji(user_id)
        return render_template("graph.html",
                               id=user_number,
                               graph_id=family_group,
                               unhide=unhide,
                               title=_("Graph"))
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=
                               _("Shuffling has not yet been done for your group (or some other error occured)!"),
                               title=
                               _("Error"),
                               no_video=True)


@graph_page.route("/graph/<event_id>/<unhide>")
@graph_page.route("/graph/<event_id>", defaults={"unhide": False})
@graph_page.route("/graph/<event_id>/", defaults={"unhide": False})
@login_required
def graph_json(event_id, unhide):
    """
    Displays an interactive graph
    """
    user_id = int(session["user_id"])

    try:
        group_id = int(event_id)
        if unhide == "True":
            user_group_admin = UserGroupAdmin.query.filter(and_(UserGroupAdmin.user_id == user_id,
                                                                UserGroupAdmin.group_id == int(group_id),
                                                                UserGroupAdmin.confirmed == True)
                                                           ).one()
            if user_group_admin is not None and user_group_admin.admin:
                unhide = True
            else:
                unhide = False

        belongs_in_group = False
        people = {"nodes": [], "links": []}
        current_year = datetime.datetime.now().year
        database_families = get_families_in_group(group_id)

        for family in database_families:
            for user in UserFamilyAdmin.query.filter(and_(UserFamilyAdmin.family_id == family.id,
                                                          UserFamilyAdmin.confirmed == True)).all():
                if unhide:
                    people["nodes"].append({"id": get_person_name(user.user_id),
                                            "group": family.id})
                else:
                    if user.user_id == user_id:
                        belongs_in_group = True
                        people["nodes"].append({"id": get_christmasy_emoji(user.user_id),
                                                "group": 2})
                    else:
                        people["nodes"].append({"id": get_christmasy_emoji(user.user_id),
                                                "group": 1})

                shuffles = Shuffle.query.filter(and_(Shuffle.giver == user.user_id, Shuffle.year == current_year)).all()
                for shuffle_element in shuffles:
                    if unhide:
                        people["links"].append({"source": get_person_name(shuffle_element.giver),
                                                "target": get_person_name(shuffle_element.getter),
                                                "value": 0})
                    else:
                        people["links"].append(
                            {"source": get_christmasy_emoji(shuffle_element.giver),
                             "target": get_christmasy_emoji(shuffle_element.getter),
                             "value": 0})

        if belongs_in_group or unhide:
            return dumps(people), 200, {"content-type": "application/json"}
        else:
            return "{}", 200, {"content-type": "application/json"}
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return "{}", 200, {"content-type": "application/json"}


@graph_page.route("/grapher/<graph_id>/<unhide>")
@graph_page.route("/grapher/<graph_id>", defaults={"unhide": ""})
@graph_page.route("/grapher/<graph_id>/", defaults={"unhide": ""})
@login_required
def graph_js(graph_id, unhide):
    """
    Returns the JS required to graph one specific graph
    """
    return render_template(
        "grapher.js",
        graph_id=graph_id,
        unhide=unhide
    ), 200, {"content-type": "application/javascript"}
