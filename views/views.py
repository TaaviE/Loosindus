# coding=utf-8
# Copyright: Taavi Eomäe 2017-2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
A simple Secret Santa website in Python
Copyright © 2017-2020 Taavi Eomäe

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
from json import dumps
from typing import List

# Cython
import pyximport

pyximport.install()

# Models
from models.events_model import ShufflingEvent
from models.family_model import Group, FamilyAdmin, GroupAdmin
from models.wishlist_model import Wishlist, wishlist_status_to_id, ArchivedWishlist

# Utilities
from logging import getLogger
from datetime import timedelta

# App specific config
from config import Config

# Flask
from flask import request, render_template, redirect, Blueprint
from flask_security import login_required
from flask_login import current_user
from flask_babelex import Domain, gettext as _

from main import babel

domain = Domain(domain="messages")
getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()


@babel.localeselector
def get_locale():
    """
    Deals with displaying the correct localization with possible override
    :return: user locale
    """
    if current_user.is_authenticated:
        user_id = session["user_id"]
    else:
        return request.accept_languages.best_match(["et", "en"])

    try:
        language_code = get_person_language_code(user_id)
    except Exception:
        return request.accept_languages.best_match(["et", "en"])

    if language_code is None:
        return request.accept_languages.best_match(["et", "en"])
    else:
        return language_code


# Database models
from models.users_model import AuthLinks

main_page = Blueprint("main_page", __name__, template_folder="templates")

# from main import sentry
from utility import *
from utility_standalone import *

# Just for assigning members_to_families a few colors
chistmasy_colors = ["#E5282A", "#DC3D2A", "#0DEF42", "#00B32C", "#0D5901"]

# Mailing
from main import security


def index():
    """
    Displays the main overview page
    """
    Domain(domain="messages")

    try:
        security.datastore.commit()
    except Exception:
        pass

    user_id = get_user_id()
    user = get_person(user_id)

    active_events: List[ShufflingEvent] = []
    inactive_events: List[ShufflingEvent] = []

    has_groups = False
    for user_family in user.families:
        for family_group in user_family.groups:
            has_groups = True
            for group_event in family_group.events:
                group_event.group_name = family_group.name
                if datetime.now() < group_event.event_at:  # If event has not taken place
                    active_events.append(group_event)
                else:
                    inactive_events.append(group_event)

    try:
        # user.last_activity_at = datetime.datetime.now()
        # user.last_activity_ip = request.headers.getlist("X-Forwarded-For")[0].rpartition(" ")[-1]
        # db.session.commit()
        pass
    except Exception as e:
        sentry_sdk.capture_exception(e)

    return render_template("index.html",
                           auth=user.first_name,
                           events=active_events,
                           uid=user_id,
                           has_groups=has_groups,
                           title=_("Home"))


@main_page.route("/shuffles")
@login_required
def shuffles():
    """
    Returns all the graphs the user could view
    """
    user_id = get_user_id()
    all_shuffles = list(Shuffle.query.filter(Shuffle.giver == user_id).all())
    active_shuffles: List[ShufflingEvent] = []
    inactive_shuffles: List[ShufflingEvent] = []
    for shuffle_pair in all_shuffles:
        shuffle_event = ShufflingEvent.query.get(shuffle_pair.event_id)
        shuffle_pair.event_name = shuffle_event.name
        shuffle_pair.group_id = shuffle_event.group_id
        shuffle_pair.group_name = Group.query.get(shuffle_event.group_id).name
        shuffle_pair.giver_name = User.query.get(shuffle_pair.giver).first_name
        shuffle_pair.getter_name = User.query.get(shuffle_pair.getter).first_name
        if datetime.now() < shuffle_event.event_at:
            active_shuffles.append(shuffle_pair)
        else:
            inactive_shuffles.append(shuffle_pair)

    return render_template("table_views/shuffles.html",
                           title=_("Shuffles"),
                           active_shuffles=active_shuffles,
                           inactive_shuffles=inactive_shuffles)


@main_page.route("/setup", methods=["GET"])
@login_required
def setup():
    """
    Provides a page where people can start setting up their
    """
    return render_template("setup.html", title=_("Setup"))


@main_page.route("/setup", methods=["POST"])
@login_required
def setup_post():
    """
    Deals with the submitted setup form
    """
    # TODO:
    return redirect()


@main_page.route("/curr_shuffle/<event_id>")
@login_required
def shuffle(event_id: str):
    """
    Returns a page that displays a specific event's curr_shuffle
    """
    user_id = get_user_id()
    user = User.query.get(user_id)
    username = user.first_name
    event_id = int(event_id)

    curr_shuffle = Shuffle.query.get((user_id, event_id))

    logger.debug("Username: {}, From: {}, To: {}", username, curr_shuffle.giver, curr_shuffle.getter)
    return render_template("shuffle.html",
                           title=_("Shuffle"),
                           id=user_id)


@main_page.route("/event/<event_id>")
@login_required
def event(event_id: str):
    """
    Displays all the families in the event
    """
    user_id = get_user_id()
    event_id = int(event_id)
    requested_event = ShufflingEvent.query.get(event_id)
    if not requested_event:
        return render_template("utility/error.html")

    requested_group: Group = Group.query.get(requested_event.group_id)
    authorized = False

    for group_family in requested_group.families:
        for member in group_family.members:
            if member.id == user_id:
                authorized = True
                break

    if not authorized:
        return render_template("utility/error.html")

    if requested_event.event_at < datetime.now():
        taken_place = True
    else:
        taken_place = False

    return render_template("table_views/families.html",
                           event=requested_event,
                           event_has_taken_place=taken_place,
                           families=requested_group.families,
                           group_id=requested_group.id,
                           title=_("Event"))


@main_page.route("/group/<group_id>")
@login_required
def group(group_id: str):
    """
    Displays all the families in the group
    """
    user_id = get_user_id()
    group_id = int(group_id)
    group = Group.query.get(group_id)
    if not group:
        return render_template("utility/error.html")

    authorized = False
    is_group_admin = False
    for group_admin in group.admins:
        if group_admin.id == user_id:
            is_group_admin = True
            authorized = True
            break

    if not authorized:
        for family in group.families:
            for member in family.members:
                if member.id == user_id:
                    authorized = True
                    break

    if not authorized:
        return render_template("utility/error.html")

    return render_template("table_views/families.html",
                           is_group_admin=is_group_admin,
                           families=group.families,
                           group_id=group.id,
                           title=_("Event"))


@main_page.route("/family/<group_id>/<family_id>")
@main_page.route("/family/<family_id>", defaults={"group_id": None})
@login_required
def family(group_id: str, family_id: str):
    """
    Displays all the people in the family
    """
    user_id = get_user_id()
    family_id = int(family_id)

    requested_family = Family.query.get(family_id)
    if not requested_family:
        return render_template("utility/error.html",
                               message=_("You do are not authorized to access this family"))

    authorized = False
    if not group_id:
        for member in requested_family.members:
            if member.id == user_id:
                authorized = True
                break
    else:
        authorized = True

    if not authorized:
        return render_template("utility/error.html",
                               message=_("You do are not authorized to access this family"))

    if group_id:
        group_id = int(group_id)
        requested_group = Group.query.get(group_id)
        if not requested_group:
            return render_template("utility/error.html",
                                   message=_("You do are not authorized to access this family"))

        authorized = False
        for member in requested_family.members:
            if member.id == user_id:
                authorized = True
                break

        if not authorized:
            for family in requested_group.families:
                for member in family.members:
                    if member.id == user_id:
                        authorized = True
                        break

        if not authorized:
            for f_group in requested_family.groups:
                for g_family in f_group.families:
                    for f_member in g_family.members:
                        if f_member.id == user_id:
                            authorized = True
                            break

        if not authorized:
            return render_template("utility/error.html",
                                   message=_("You do are not authorized to access this family"))

    return render_template("table_views/users.html",
                           members=requested_family.members,
                           family_id=family_id,
                           group_id=group_id,
                           title=_("Family"))


@main_page.route("/events")
@login_required
def events():
    """
    Displays all the events of a person
    """
    user = get_user()

    events: List[ShufflingEvent] = []
    for family in user.families:
        for group in family.groups:
            for event in group.events:
                events.append(event)

    return render_template("table_views/events.html",
                           events=events)


@main_page.route("/reminders")
@login_required
def reminders():
    """
    Displays all the reminders that concern a group
    """

    return render_template("table_views/reminders.html",
                           events=events)


@main_page.route("/notifications")
@login_required
def notifications():
    """
    Displays all the notifications for an user
    """

    return render_template("table_views/notifications.html",
                           events=events)


@main_page.route("/subscriptions")
@login_required
def subscriptions():
    """
    Displays all the notifications for an user
    """

    return render_template("table_views/subscriptions.html",
                           events=events)


@main_page.route("/families")
@login_required
def families():
    """
    Displays all the families of a person
    """

    user = get_user()

    return render_template("table_views/families.html",
                           group_id=None,
                           title=_("Families"),
                           families=user.families)


@main_page.route("/groups")
@login_required
def groups():
    """
    Displays all the groups of a person
    """
    user = get_user()

    groups = []
    for family in user.families:
        for group in family.groups:
            groups.append(group)

    # There's probably a better way to get all groups
    admined_groups: List[GroupAdmin] = GroupAdmin.query.filter(GroupAdmin.user_id == user.id).all()
    if len(admined_groups) <= 0:
        admined_groups = None

    admined_groups_objects: List[Group] = []
    for admined_group in admined_groups:
        admined_groups_objects.append(Group.query.get(admined_group.group_id))

    return render_template("table_views/groups.html",
                           groups=groups,
                           administered_groups=admined_groups_objects)


@main_page.route("/notes")
@login_required
def notes():
    """
    Displays all the notes in one's wishlist
    """
    user_id = session["user_id"]
    # username = get_person_name(user_id)
    empty = False

    try:
        # noinspection PyComparisonWithNone
        # SQLAlchemy doesn't like "is None"
        db_notes = Wishlist.query.filter(Wishlist.user_id == user_id).all()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise e

    if len(db_notes) <= 0:
        empty = True

    return render_template("table_views/notes_private.html",
                           list=db_notes,
                           empty=empty,
                           datetime=datetime,
                           timedelta=timedelta,
                           title=_("My Wishlist"))


@main_page.route("/archivednotes")
@login_required
def archived_notes():
    """
    Displays all the archived notes in one's wishlist
    """
    user_id = session["user_id"]
    # username = get_person_name(user_id)
    notes_from_file = {}
    empty = False

    try:
        # noinspection PyComparisonWithNone
        # SQLAlchemy doesn't like "is None"
        db_notes = ArchivedWishlist.query.filter(ArchivedWishlist.user_id == user_id).all()
        for note in db_notes:
            notes_from_file[note.item] = note.id
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise e

    if len(notes_from_file) <= 0:
        notes_from_file = {_("Right now there's nothing in the Wishlist"): ("", "")}
        empty = True

    return render_template("table_views/notes_private_archived.html",
                           list=notes_from_file,
                           empty=empty,
                           title=_("My Wishlist"))


@main_page.route("/wishlist/<group_id>/<person_id>")
@main_page.route("/wishlist/<person_id>")
@login_required
def wishlist(person_id: str, group_id: str = None):
    """
    Display specific user's wishlist
    """
    user_id = int(session["user_id"])
    user = User.query.get(user_id)
    invalid_notes = False

    if not person_id.isnumeric():
        return render_template("utility/error.html",
                               no_sidebar=False,
                               message=_("Access denied"),
                               title=_("Access denied"))

    person_id = int(person_id)
    if person_id == user_id:
        return render_template("utility/error.html",
                               no_sidebar=False,
                               message=_("To view your own list use the sidebar"),
                               title=_("Access denied"))

    target_user = User.query.get(person_id)
    first_name = target_user.first_name

    if group_id:  # If group is given let's check if the person may access trough group
        if not group_id.isnumeric():
            return render_template("utility/error.html",
                                   no_sidebar=False,
                                   message=_("Access denied"),
                                   title=_("Access denied"))

        group_id = int(group_id)
        group = Group.query.get(group_id)
        if not group:
            return render_template("utility/error.html",
                                   no_sidebar=False,
                                   message=_("To view your own list use the sidebar"),
                                   title=_("Access denied"))

        authorized = False
        for user_family in group.families:
            for member in user_family.members:
                if member.id == user.id:
                    authorized = True
                    break

        if not authorized:
            return render_template("utility/error.html",
                                   no_sidebar=False,
                                   message=_("Not authorized"),
                                   title=_("Access denied"))
    else:  # Group wasn't given, if the person isn't in the family then forbidden
        authorized = False
        for user_family in user.families:
            for member in user_family.members:
                if member.id == user_id:
                    authorized = True
                    break

        if not authorized:
            return render_template("utility/error.html",
                                   no_sidebar=False,
                                   message=_("Not authorized"),
                                   title=_("Access denied"))

    currentnotes = []
    try:
        logger.info("{} is opening wishlist of {}".format(user_id, target_user.id))
        # noinspection PyComparisonWithNone
        db_notes: List[Wishlist] = Wishlist.query.filter(Wishlist.user_id == target_user.id).all()
        if len(db_notes) <= 0:
            raise Exception("Not a single wishlist item")

        for note in db_notes:
            all_states = list(wishlist_status_to_id.items())
            all_states.remove(("modified", wishlist_status_to_id["modified"]))
            selections = []
            modifyable = False
            name = ""

            if note.status == wishlist_status_to_id["default"] or note.status is None:
                selections = all_states
                selections.remove(("default", wishlist_status_to_id["default"]))
                selections.insert(0, ("default", wishlist_status_to_id["default"]))
                modifyable = True
            elif note.status == wishlist_status_to_id["modified"]:
                if note.purchased_by == user_id or note.purchased_by is None:
                    selections = all_states
                    selections.insert(0, ("modified", wishlist_status_to_id["modified"]))
                    modifyable = True
                else:
                    selections = [("modified", wishlist_status_to_id["modified"])]
                    modifyable = False
                name = get_christmasy_emoji(note.purchased_by)
            elif note.status == wishlist_status_to_id["purchased"]:
                selections = [("purchased", wishlist_status_to_id["purchased"])]
                name = get_christmasy_emoji(note.purchased_by)
                modifyable = False
            elif note.status == wishlist_status_to_id["booked"]:
                selections = [("booked", wishlist_status_to_id["booked"]),
                              ("default", wishlist_status_to_id["default"]),
                              ("purchased", wishlist_status_to_id["purchased"])]
                name = get_christmasy_emoji(note.purchased_by)
                if note.purchased_by == user_id:
                    modifyable = True
                else:
                    modifyable = False

            note.buyer = name
            note.statuses = selections
            note.status_modifyable = modifyable
            currentnotes.append(note)
    except ValueError as e:
        sentry_sdk.capture_exception(e)
    except Exception as e:
        currentnotes = []
        invalid_notes = True
        logger.info("Error displaying notes, there might be none: {}".format(e))

    return render_template("table_views/notes_public.html",
                           notes=currentnotes,
                           target=get_name_in_genitive(first_name),
                           id=group_id,
                           title=_("Wishlist"),
                           invalid=invalid_notes,
                           back=True)


@main_page.route("/graph")
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


@main_page.route("/graph/<event_id>/<unhide>")
@main_page.route("/graph/<event_id>", defaults={"unhide": False})
@main_page.route("/graph/<event_id>/", defaults={"unhide": False})
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
            if user_group_admin is not None and user_group_admin.creator:
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


@main_page.route("/grapher/<graph_id>/<unhide>")
@main_page.route("/grapher/<graph_id>", defaults={"unhide": ""})
@main_page.route("/grapher/<graph_id>/", defaults={"unhide": ""})
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


@main_page.route("/settings")
@login_required
def settings():
    """
    Displays a settings page
    """
    user_id: int = int(session["user_id"])
    user: User = User.query.get(user_id)

    if len(user.families) > 0:
        is_in_family = True
    else:
        is_in_family = False

    user_families = {}
    family_admin = False
    for family in user.families:
        if user in family.admins:
            if FamilyAdmin.query.get(user_id=user.id, family_id=family.id).creator:
                family_admin = True

    user_groups = {}
    is_in_group = False
    group_admin = False
    for family in user.families:
        for group_relationship in family.groups:
            if user in group_relationship.admins:
                curr_group = GroupAdmin.query.get(user_id=user.id, group_id=group_relationship.id)
                if curr_group.creator:
                    user_groups[group_relationship.description] = (group_relationship.id, True)
                    group_admin = True
                else:
                    user_groups[group_relationship.description] = (group_relationship.id, False)

            is_in_group = True

    id_link_exists = False
    google_link_exists = False
    github_link_exists = False  # TODO: Store them all in a dictionary and render based on that
    facebook_link_exists = False
    try:
        user_links = AuthLinks.query.filter(AuthLinks.user_id == int(user_id)).all()
        for link in user_links:
            if "esteid" == link.provider:
                id_link_exists = True
            elif "google" == link.provider:
                google_link_exists = True
            elif "github" == link.provider:
                github_link_exists = True
            elif "facebook" == link.provider:
                facebook_link_exists = True
    except Exception as e:
        sentry_sdk.capture_exception(e)

    return render_template("settings.html",
                           user_id=user_id,
                           user_name=user.first_name,
                           user_language=user.language,
                           in_family=is_in_family,
                           in_group=is_in_group,
                           families=user_families,
                           groups=user_groups,
                           title=_("Settings"),
                           id_connected=id_link_exists,
                           google_connected=google_link_exists,
                           github_connected=github_link_exists,
                           facebook_connected=facebook_link_exists,
                           group_admin=group_admin,
                           family_admin=family_admin)
