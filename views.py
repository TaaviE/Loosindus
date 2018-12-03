#!/usr/bin/python3
# coding=utf-8
# author=Taavi Eomäe
"""
A simple Secret Santa website in Python
Copyright (C) 2017-2018 Taavi Eomäe

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

#####
# TODO:
# * 
#
# Known flaws:
# * SecretSanta can't match less than two people or people from less than one family
####

from logging import getLogger

# Graphing
import secretsanta
# App specific config
from config import Config
from models.users_model import Links

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()

# Utilities
import copy

# Flask
from flask import g, request, render_template, session, redirect, send_from_directory, Blueprint
from flask_security import login_required, logout_user
from flask_login import current_user, login_user
from flask_mail import Message

# Translation
# Try switching between babelex and babel if you are getting errors
from flask_babelex import gettext as _
from flask_babelex import Domain

domain = Domain(domain="messages")

from main import babel


@babel.localeselector
def get_locale():
    if "user_id" in session.keys():  # If logged in
        user_id = session["user_id"]
    else:
        return request.accept_languages.best_match(["et", "en"])
    language_code = get_person_language_code(user_id)
    if language_code is None:
        return request.accept_languages.best_match(["et", "en"])
    else:
        return language_code


# Database models
from main import db
from models.wishlist_model import NoteState
from models.family_model import Family
from models.groups_model import Groups
from models.user_group_admin_model import UserGroupAdmin

main_page = Blueprint("main_page", __name__, template_folder="templates")

from main import sentry

from utility import *

set_recursionlimit()

# Just for assigning members_to_families a few colors
chistmasy_colors = ["#E5282A", "#DC3D2A", "#0DEF42", "#00B32C", "#0D5901"]

# Mailing
from main import celery, security, mail


# Send asynchronous email
@celery.task
def send_security_email(msg):
    mail.send(msg)


# Override security email sender
@security.send_mail_task
def delay_security_email(msg):
    send_security_email.delay(msg)


# Show a friendlier error page
@main_page.errorhandler(500)
def error_500(err):
    try:
        if not current_user.is_authenticated:
            sentry_enabled = False
        else:
            sentry_enabled = True
    except Exception:
        sentry_enabled = False
    return render_template("error.html",
                           sentry_enabled=sentry_enabled,
                           sentry_ask_feedback=True,
                           sentry_event_id=g.sentry_event_id,
                           sentry_public_dsn=sentry.client.get_public_dsn("https"),
                           message=_("There was an error"),
                           title=_("Error"))


@main_page.errorhandler(404)
def error_404(err):
    try:
        if not current_user.is_authenticated:
            sentry_enabled = False
        else:
            sentry_enabled = True
    except Exception:
        sentry_enabled = False
    return render_template("error.html",
                           sentry_enabled=sentry_enabled,
                           sentry_ask_feedback=True,
                           sentry_event_id=g.sentry_event_id,
                           sentry_public_dsn=sentry.client.get_public_dsn("https"),
                           message=_("Page not found!"),
                           title=_("Error"))


# Views
@main_page.route("/test")
@login_required
def test():
    check = check_if_admin()
    if check is not None:
        return check
    # remind_about_change(False)
    # remind_to_buy(False)
    # remind_to_add(False)
    return render_template("error.html",
                           message=_("Here you go!"),
                           title=_("Error"))


@main_page.route("/favicon.ico")
def favicon():
    return send_from_directory("./static",
                               "favicon-16x16.png")


def index():
    domain = Domain(domain="messages")  # Uncomment this when using babelex

    try:
        security.datastore.commit()
    except Exception:
        pass

    user_id = session["user_id"]
    username = get_person_name(user_id)
    no_shuffle = False
    if get_target_id(user_id) == -1:
        no_shuffle = True

    try:
        user = User.query.get(int(user_id))
        user.last_activity_at = datetime.datetime.now()
        user.last_activity_ip = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
        db.session.commit()
    except Exception as e:
        sentry.captureException(e)

    return render_template("index.html",
                           auth=username,
                           no_shuffle=no_shuffle,
                           uid=user_id,
                           title=_("Home"))


@main_page.route("/about")
def about():
    return render_template("home.html",
                           no_sidebar=True)


@main_page.route("/")
def home():
    if current_user.is_authenticated:
        return index()
    else:
        return about()


@main_page.route("/contact")
def contact():
    return render_template("contact.html",
                           no_sidebar=True)


@main_page.route("/robots.txt")
def robots():
    return send_from_directory("./static",
                               "robots.txt")


@main_page.route("/sitemap.xml")
def sitemap():
    return send_from_directory("./static",
                               "sitemap.xml")


@main_page.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@main_page.route("/shuffle")
@login_required
def shuffle():
    user_id = session["user_id"]
    username = get_person_name(user_id)
    info(username)
    gifter = get_person_id(username)
    info(gifter)
    giftee = get_target_id(gifter)
    info(giftee)
    return render_template("shuffle.html",
                           title=_("Shuffle"),
                           id=giftee)


@main_page.route("/notes")
@login_required
def notes():
    user_id = session["user_id"]
    # username = get_person_name(user_id)
    notes_from_file = {}
    empty = False

    try:
        db_notes = Wishlist.query.filter(Wishlist.user_id == user_id).all()
        for note in db_notes:
            notes_from_file[note.item] = encrypt_id(note.id)
    except Exception as e:
        if not Config.DEBUG:
            sentry.captureException()
        raise e

    if len(notes_from_file) <= 0:
        notes_from_file = {_("Right now there's nothing in the Wishlist"): ("", "")}
        empty = True

    return render_template("notes.html",
                           list=notes_from_file,
                           empty=empty,
                           title=_("My Wishlist"))


@main_page.route("/createnote", methods=["GET"])
@login_required
def createnote():
    return render_template("createnote.html",
                           title=_("Add new"))


@main_page.route("/createnote", methods=["POST"])
@login_required
def createnote_add():
    logger.info("Got a post request to add a note")
    user_id = session["user_id"]
    username = get_person_name(user_id)
    logger.info("Found user:", username)
    logger.info("Found user id:", user_id)
    currentnotes = {}
    addednote = request.form["note"]

    if len(addednote) > 1000:
        return render_template("error.html",
                               message=_("Pls no hax ") + username + "!!",
                               title=_("Error"))
    elif len(addednote) <= 0:
        return render_template("error.html",
                               message=_("Santa can't bring you nothin', ") + username + "!",
                               title=_("Error"))

    logger.info("Trying to add a note:", addednote)
    try:
        logger.info("Opening file", user_id)
        #    with open("./notes/" + useridno, "r") as file:
        #        currentnotes = json.load(file)
        db_notes = Wishlist.query.filter(Wishlist.user_id == user_id).all()
        for note in db_notes:
            currentnotes[note.item] = note.id
    except Exception as e:
        if not Config.DEBUG:
            sentry.captureException()
        raise e

    if len(currentnotes) >= 200:
        return render_template("error.html",
                               message=_("You're wishing for too much, ") + username + "",
                               title=_("Error"))

    db_entry_notes = Wishlist(
        user_id=user_id,
        item=addednote
    )

    try:
        db.session.add(db_entry_notes)
        db.session.commit()
    except Exception as e:
        if not Config.DEBUG:
            sentry.captureException()
        raise e

    return render_template("success.html",
                           action=_("Added"),
                           link="./notes",
                           title=_("Added"))


@main_page.route("/editnote", methods=["GET"])
@login_required
def editnote():
    user_id = session["user_id"]
    username = get_person_name(user_id)

    try:
        request_id = request.args["id"]
        request_id = decrypt_id(request_id)
        request_id = int(request_id)

        info(user_id, "is trying to remove a note", request_id)
    except Exception:
        if not Config.DEBUG:
            sentry.captureException()
        return render_template("error.html",
                               message=_("Pls no hax ") + username + "!!",
                               title=_("Error"))

    try:
        info(user_id, " is editing notes of ", request_id)
        db_note = Wishlist.query.get(request_id)
    except Exception as e:
        if not Config.DEBUG:
            sentry.captureException()
        raise e

    return render_template("createnote.html",
                           action=_("Edit"),
                           title=_("Edit"),
                           placeholder=db_note.item)


@main_page.route("/editnote", methods=["POST"])
@login_required
def editnote_edit():
    logger.info("Got a post request to edit a note by")
    user_id = session["user_id"]
    # username = get_person_name(user_id)
    logger.info(" user id:", user_id)

    addednote = request.form["note"]
    try:
        request_id = request.args["id"]
        request_id = decrypt_id(request_id)
        request_id = int(request_id)
    except Exception:
        if not Config.DEBUG:
            sentry.captureException()
        return render_template("error.html",
                               message=_("Broken link"),
                               title=_("Error"))

    db_note = Wishlist.query.get(request_id)

    try:
        db_note.item = addednote
        db_note.status = NoteState.MODIFIED.value["id"]
        db.session.commit()
    except Exception as e:
        if not Config.DEBUG:
            sentry.captureException()
        db.session.rollback()
        raise e

    return render_template("success.html",
                           action=_("Changed"),
                           link="./notes",
                           title=_("Changed"))


@main_page.route("/removenote")
@login_required
def deletenote():
    user_id = session["user_id"]
    username = get_person_name(user_id)

    try:
        request_id = request.args["id"]
        request_id = decrypt_id(request_id)
        request_id = int(request_id)
        info(user_id, " is trying to remove a note", request_id)
    except Exception:
        if not Config.DEBUG:
            sentry.captureException()
        return render_template("error.html",
                               message=_("Broken link"),
                               title=_("Error"))

    try:
        Wishlist.query.filter_by(id=request_id).delete()
        db.session.commit()
    except Exception:
        if not Config.DEBUG:
            sentry.captureException()
        return render_template("error.html",
                               message=_("Can't find what you wanted to delete"),
                               title=_("Error"))

    #    with open("./notes/" + useridno, "w") as file:
    #        file.write(json.dumps(currentnotes))

    logger.info("Removed", username, "note with ID", request_id)
    return render_template("success.html",
                           action=_("Removed"),
                           link="./notes",
                           title=_("Removed"))


@main_page.route("/giftingto", methods=["POST"])
@login_required
def updatenotestatus():
    user_id = session["user_id"]
    try:
        status = int(request.form["status"])
        note = Wishlist.query.get(decrypt_id(request.form["id"]))

        if status > -1:
            if int(note.status) == NoteState.PURCHASED.value["id"] or status == \
                    NoteState.MODIFIED.value["id"]:
                raise Exception("Invalid access")
            note.status = status
            note.purchased_by = user_id
            db.session.commit()
        #        elif status == "off":
        #            note.status = NoteState.DEFAULT.value["id"]
        #            note.purchased_by = None
        elif status == -1:
            if int(note.status) == NoteState.PURCHASED.value["id"] or status == \
                    NoteState.MODIFIED.value["id"]:
                raise Exception("Invalid access")
            note.status = status
            note.purchased_by = None
            db.session.commit()
        else:
            raise Exception("Invalid status code")
    except Exception as e:
        if not Config.DEBUG:
            sentry.captureException()
        else:
            logger.info("Failed toggling:", e)
        return render_template("error.html",
                               message=_("Could not edit"),
                               title=_("Error"),
                               back=True)

    #    with open("./notes/" + useridno, "w") as file:
    #        file.write(json.dumps(currentnotes))

    return redirect("/giftingto?id=" + str(request.args["id"]), code=303)


christmasy_emojis = ["🎄", "🎅", "🤶", "🦌", "🍪", "🌟", "❄️", "☃️", "⛄", "🎁", "🎶", "🕯️", "🔥", "🥶", "🧣", "🧥",
                     "🌲", "🌁", "🌬️", "🎿", "🏔️", "🌨️", "🏂", "⛷️"]


def get_christmasy_emoji(user_id):
    """
    :type user_id: int
    """
    if user_id is not None:
        emoji = christmasy_emojis[user_id % len(christmasy_emojis)]
    else:
        emoji = ""
    return emoji


@main_page.route("/giftingto")
@login_required
def giftingto():
    check = check_if_admin()
    # if check is not None:
    #   return check

    user_id = session["user_id"]
    username = get_person_name(user_id)
    invalid_notes = False

    try:
        back_count = request.args["back"]
    except Exception:
        back_count = -1

    try:
        request_id = request.args["id"]
        request_id = int(decrypt_id(request_id))
    except Exception as e:
        logger.info("Failed decrypting or missing:", e)
        request_id = get_target_id(user_id)

    try:  # Yeah, only valid IDs please
        if request_id == -1:
            return render_template("error.html",
                                   message=_("Shuffling has not yet been done for your group!"),
                                   title=_("Error"))
        elif request_id < 0:
            raise Exception()
        elif request_id == int(user_id):
            return render_template("error.html",
                                   message=_("Access to this list is forbidden"),
                                   title=_("Forbidden"))
    except Exception:
        if not Config.DEBUG:
            sentry.captureException()
        return render_template("error.html",
                               message=_("Pls no hax ") + username + "!!",
                               title=_("Error"))

    if check is not None:  # Let's not let everyone read everyone's lists
        if request_id != get_target_id(user_id):
            family_id = get_family_id(user_id)
            family_obj = Family.query.get(family_id)
            family_group = family_obj.group

            database_all_families_with_members = []
            database_families = Family.query.filter(Family.group == family_group).all()
            for db_family in database_families:
                database_family_members = UserFamilyAdmin.query.filter(
                    UserFamilyAdmin.family_id == db_family.id).all()
                database_all_families_with_members.append(database_family_members)

            found = False
            for family in database_all_families_with_members:
                for member in family:
                    if member.user_id == request_id:
                        found = True

            if not found:
                return check

    currentnotes = {}

    try:
        info(user_id, "is opening file:", request_id)
        db_notes = Wishlist.query.filter(Wishlist.user_id == request_id).all()
        if len(db_notes) <= 0:
            raise Exception

        for note in db_notes:
            all_states = [state.value for state in NoteState]
            all_states.remove(NoteState.MODIFIED.value)
            selections = []
            modifyable = False
            name = ""

            if note.status == NoteState.DEFAULT.value["id"]:
                selections = all_states
                selections.insert(0, selections.pop(selections.index(NoteState.DEFAULT.value)))
                modifyable = True
            elif note.status == NoteState.MODIFIED.value["id"]:
                if note.purchased_by == int(user_id) or note.purchased_by is None:
                    selections = all_states
                    selections.insert(0, NoteState.MODIFIED.value)
                    modifyable = True
                else:
                    selections = [NoteState.MODIFIED.value]
                    modifyable = False
                name = get_christmasy_emoji(note.purchased_by)
            elif note.status == NoteState.PURCHASED.value["id"]:
                selections = [NoteState.PURCHASED.value]
                name = get_christmasy_emoji(note.purchased_by)
                modifyable = False
            elif note.status == NoteState.PLANNING_TO_PURCHASE.value["id"]:
                selections = [NoteState.PLANNING_TO_PURCHASE.value,
                              NoteState.DEFAULT.value, NoteState.PURCHASED.value]
                name = get_christmasy_emoji(note.purchased_by)
                if note.purchased_by == int(user_id):
                    modifyable = True
                else:
                    modifyable = False

            currentnotes[note.item] = (encrypt_id(note.id), copy.deepcopy(selections), modifyable, name)
    except ValueError:
        if not Config.DEBUG:
            sentry.captureException()
    except Exception as e:
        currentnotes = {_("Right now there isn't anything on the list"): (-1, -1, False, "")}
        invalid_notes = True
        logger.info("Error displaying notes, there might be none:", e)

    return render_template("show_notes.html",
                           notes=currentnotes,
                           target=get_name_in_genitive(get_person_name(request_id)),
                           id=encrypt_id(request_id),
                           title=_("Wishlist"),
                           invalid=invalid_notes,
                           back=True,
                           back_count=back_count)


@main_page.route("/graph")
@login_required
def graph():
    user_id = session["user_id"]
    try:
        family_id = get_family_id(user_id)
        family_obj = Family.query.get(family_id)
        family_group = family_obj.group
        if "unhide" in request.args.keys():  # Make prettier
            if request.args["unhide"] in "True":
                unhide = "/True"
                user_number = _("or with your own name")
            else:
                unhide = ""
                user_number = str(user_id)
        else:
            unhide = ""
            user_number = str(user_id)
        return render_template("graph.html",
                               id=get_christmasy_emoji(user_number),
                               graph_id=family_group,
                               unhide=unhide,
                               title=_("Graph"))
    except Exception:
        return render_template("error.html",
                               message=_("Shuffling has not yet been done for your group!"),
                               title=_("Error"))


@main_page.route("/graph/<graph_id>/<unhide>")
@main_page.route("/graph/<graph_id>", defaults={"unhide": False})
@login_required
def graph_json(graph_id, unhide):
    user_id = int(session["user_id"])
    if unhide is "True":
        if UserGroupAdmin.query.filter(UserGroupAdmin.user_id == user_id).first() is not None:
            unhide = True
        else:
            unhide = False

    try:
        graph_id = int(graph_id)
        belongs_in_group = False
        people = {"nodes": [], "links": []}
        for family in Family.query.filter(Family.group == graph_id).all():
            for user in UserFamilyAdmin.query.filter(UserFamilyAdmin.family_id == family.id).all():
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

                shuffles = Shuffle.query.filter(Shuffle.giver == user.user_id).all()
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
            return "{}"
    except Exception as e:
        sentry.captureException(e)
        return "{}"


@main_page.route("/grapher/<graph_id>/<unhide>")
@main_page.route("/grapher/<graph_id>", defaults={"unhide": ""})
@login_required
def graph_js(graph_id, unhide):
    return render_template("grapher.js", graph_id=graph_id, unhide=unhide), \
           200, \
           {"content-type": "application/javascript"}


@main_page.route("/settings")
@login_required
def settings():
    user_id = session["user_id"]
    user_obj = User.query.get(user_id)
    is_in_group = False
    is_in_family = False

    db_families_user_has_conn = UserFamilyAdmin.query.filter(
        UserFamilyAdmin.user_id == user_id).all()

    user_families = {}
    db_groups_user_has_conn = []
    for family_relationship in db_families_user_has_conn:
        family = Family.query.get(family_relationship.family_id)
        user_families[family.name] = (encrypt_id(family.id), family_relationship.admin)
        is_in_family = True
        db_groups_user_has_conn += (Groups.query.filter(Family.group == family.group).all())

    user_groups = {}
    for group_relationship in db_groups_user_has_conn:
        group_admin = UserGroupAdmin.query.filter(
            UserGroupAdmin.user_id == user_id
            and
            UserGroupAdmin.group_id == group_relationship.id).first()

        if not group_admin:
            user_groups[group_relationship.description] = (encrypt_id(group_relationship.id), False)
        else:
            user_groups[group_relationship.description] = (encrypt_id(group_relationship.id), group_admin.admin)
        is_in_group = True

    id_link_exists = False
    try:
        user_links = Links.query.filter(Links.user_id == int(user_id)).all()
        for link in user_links:
            if "serialNumber" in link.provider_user_id:
                id_link_exists = True
    except Exception as e:
        sentry.captureException(e)

    return render_template("settings.html",
                           user_id=user_id,
                           user_name=user_obj.username,
                           user_language=user_obj.language,
                           family_admin=is_in_family,
                           group_admin=is_in_group,
                           families=user_families,
                           groups=user_groups,
                           title=_("Settings"),
                           id_connected=id_link_exists,
                           back_link="/")


@main_page.route("/editfam")
@login_required
def editfamily():
    user_id = session["user_id"]

    try:
        request_id = request.args["id"]
        request_id = int(decrypt_id(request_id))
    except Exception:
        if not Config.DEBUG:
            sentry.captureException()
        return render_template("error.html",
                               message=_("Broken link"),
                               title=_("Error"))

    if request_id < 0:
        if not Config.DEBUG:
            sentry.captureException()
        return render_template("error.html",
                               message=_("Broken link"),
                               title=_("Error"))

    db_family_members = UserFamilyAdmin.query.filter(
        UserFamilyAdmin.family_id == request_id).all()

    family = []
    show_admin_column = False
    for member in db_family_members:
        is_admin = False
        is_person = False
        if member.user_id == user_id:
            is_person = True

        family.append((get_person_name(member.user_id), encrypt_id(member.user_id), is_admin, is_person))

    return render_template("editfam.html",
                           family=family,
                           title=_("Edit family"),
                           admin=show_admin_column,
                           back=False,
                           back_link="/settings")


@main_page.route("/setlanguage", methods=["POST"])
@login_required
def set_language():
    user_id = session["user_id"]
    try:
        if request.form["language"] in ["en", "ee"]:
            user = User.query.filter(User.id == user_id).first()
            try:
                user.language = request.form["language"]
                db.session.commit()
            except Exception as e:
                sentry.captureException(e)
                db.session.rollback()
                return render_template("error.html",
                                       message=_("Faulty input"),
                                       title=_("Error"))

        return render_template("success.html",
                               action=_("Added"),
                               link="./notes",
                               title=_("Added"))
    except Exception:
        # No need to capture with Sentry, someone's just meddling
        return render_template("error.html",
                               message=_("Faulty input"),
                               title=_("Error"))


@main_page.route("/editfam", methods=["POST"])
@login_required
def editfamily_with_action():
    # TODO:
    # user_id = session["user_id"]

    # try:
    # action = request.args["action"]
    # request_id = request.args["id"]
    # request_id = int(decrypt_id(request_id))
    # except Exception:
    # return render_template("error.html", message="Tekkis viga, kontrolli linki", title="Error")

    return None


@main_page.route("/editgroup")
@login_required
def editgroup():
    user_id = session["user_id"]
    # user_obj = User.query.get(user_id)

    try:
        request_id = request.args["id"]
        request_id = int(decrypt_id(request_id))
    except Exception:
        if not Config.DEBUG:
            sentry.captureException()
        request_id = 0

    db_groups_user_is_admin = UserGroupAdmin.query.filter(
        UserGroupAdmin.user_id == user_id).all()

    db_groups_user_has_conn = Family.query.filter(Family.group == request_id).all()

    db_group = db_groups_user_has_conn[request_id]

    db_families_in_group = Family.query.filter(Family.group == db_group.group).all()

    families = []
    for family in db_families_in_group:
        admin = False

        if family in db_groups_user_is_admin:
            admin = True

        families.append((family.name, encrypt_id(family.id), admin))

    is_admin = False
    if len(db_groups_user_is_admin) > 0:
        is_admin = True

    return render_template("editgroup.html",
                           title=_("Edit group"),
                           families=families,
                           admin=is_admin)


@main_page.route("/editgroup", methods=["POST"])
@login_required
def editgroup_with_action():
    # TODO:
    # user_id = session["user_id"]
    # user_obj = User.query.get(user_id)
    return None


@main_page.route("/secretgraph")
@login_required
def secretgraph():
    check = check_if_admin()
    if check is not None:
        return check

    request_id = str(request.args["id"])

    return render_template("graph.html",
                           id=str(get_person_name(session["user_id"])),
                           image="s" + request_id + ".png",
                           title=_("Secret graph"))


def check_if_admin():
    user_id = session["user_id"]
    requester = get_person_name(user_id)
    requester = requester.lower()

    if requester != "admin" and requester != "taavi":
        return render_template("error.html",
                               message=_("Pls no hax ") + requester + "!!",
                               title=_("Error"))
    else:
        return None


"""@main_page.route("/family")
@login_required
def family():
    user_id = session["user_id"]
    family_id = User.query.get(user_id).family_id
    family_members = User.query.filter(User.family_id == family_id).all()
    family_member_names = []
    for member in family_members:
        family_member_names.append(member.username)
    return render_template("show_family.html", names=family_member_names, title="Perekond")
"""


@main_page.route("/recreategraph")
@login_required
def regraph():
    check = check_if_admin()
    if check is not None:
        return check

    user_id = session["user_id"]
    family_id = get_family_id(user_id)
    family_obj = Family.query.get(family_id)
    family_group = family_obj.group

    database_families = Family.query.filter(Family.group == family_group).all()
    database_all_families_with_members = []
    for db_family in database_families:
        database_family_members = UserFamilyAdmin.query.filter(
            UserFamilyAdmin.family_id == db_family.id).all()
        database_all_families_with_members.append(database_family_members)

    families = []
    family_ids_map = {}
    for family_index, list_family in enumerate(database_all_families_with_members):
        families.insert(family_index, {})
        for person_index, person in enumerate(list_family):
            family_ids_map[family_index] = get_family_id(person.user_id)
            families[family_index][get_person_name(person.user_id)] = person.user_id

    families_shuf_nam = {}
    families_shuf_ids = {}
    #    logger.info("Starting finding matches")
    """""
    # This comment block contains self-written algorithm that isn't as robust 
    # as the library's solution thus this is not used for now
    
    families_give_copy = copy.deepcopy(families)  # Does the person need to give a gift
    for family_index, family_members in enumerate(families_give_copy):
        for person in family_members:
            families_give_copy[family_index][person] = True

    families_take_copy = copy.deepcopy(families)  # Does the person need to take a gift
    for family_index, family_members in enumerate(families_take_copy):
        for person in family_members:
            families_take_copy[family_index][person] = True
    
    for index, family in enumerate(families_list_copy):  # For each family among every family
        for person in family:  # For each person in given family
            if families_give_copy[index][person] == True:  # If person needs to gift
                #                print("Looking for a match for:", person, get_person_id(person))
                familynumbers = list(range(0, index))
                familynumbers.extend(range(index + 1, len(family) - 1))
                
                random.shuffle(familynumbers)
                for number in familynumbers:
                    receiving_family_index = number
                    receiving_family = families_take_copy[number]  # For each receiving family
                    #                    print("Looking at other members_to_families:", receiving_family)

                    for receiving_person in receiving_family:  # For each person in other family
                        if families_take_copy[receiving_family_index][receiving_person] == True and \
                                families_give_copy[index][person] == True:  # If person needs to receive
                            families_take_copy[receiving_family_index][receiving_person] = False  
                            #print("Receiving:", receiving_family_index, receiving_person)
                            families_give_copy[index][person] = False  # ; print("Giving:", index, person)
                            families_shuf_nam[person] = receiving_person
                            families_shuf_ids[get_person_id(person)] = get_person_id(receiving_person)
                            #                             print("Breaking")
                            break
    """""

    members_to_families = {}
    for family_id, family_members in enumerate(families):
        for person, person_id in family_members.items():
            members_to_families[person_id] = family_id

    families_to_members = {}
    for family_id, family_members in enumerate(families):
        families_to_members[family_id] = set()
        for person, person_id in family_members.items():
            currentset = families_to_members[family_id]
            currentset.update([person_id])

    last_connections = secretsanta.ConnectionGraph.ConnectionGraph(members_to_families, families_to_members)
    # connections.add(source, target, year)
    current_year = datetime.datetime.now().year
    info(current_year, "is the year of Linux Desktop")

    santa = secretsanta.secretsanta.SecretSanta(families_to_members, members_to_families, last_connections)
    new_connections = santa.generate_connections(current_year)

    shuffled_ids_str = {}
    for connection in new_connections:
        families_shuf_ids[connection.source] = connection.target
        families_shuf_nam[get_person_name(connection.source)] = get_person_name(connection.target)
        shuffled_ids_str[str(connection.source)] = str(connection.target)

        #    info( shuffled_names)
        #    info( shuffled_ids)

    for giver, getter in families_shuf_ids.items():  # TODO: Add date
        db_entry_shuffle = Shuffle(
            giver=giver,
            getter=getter,
        )
        try:
            db.session.add(db_entry_shuffle)
            db.session.commit()
        except Exception:
            db.session.rollback()
            row = Shuffle.query.get(giver)
            row.getter = getter
            db.session.commit()

    return render_template("success.html",
                           action=_("Generated"),
                           link="./notes",
                           title=_("Generated"))


@main_page.route("/testmail")
@login_required
def test_mail():
    from main import mail
    with mail.connect() as conn:
        info(conn.configure_host().vrfy)
        msg = Message(recipients=["root@localhost"],
                      body="test",
                      subject="test2")

        conn.send(msg)
    return render_template("success.html",
                           action=_("Sent"),
                           link="./testmail",
                           title=_("Sent"))


@main_page.route("/clientcert")
def log_user_in_with_cert():
    """
    This functionality requires another subdomain requiring client cert

    proxy_set_header Tls-Client-Secret Config.TLS_PROXY_SECRET;
    proxy_set_header Tls-Client-Verify $ssl_client_verify;
    proxy_set_header Tls-Client-Dn     $ssl_client_s_dn;
    proxy_set_header Tls-Client-Cert   $ssl_client_cert;
    """
    if "Tls-Client-Secret" in request.headers.keys():
        logger.debug("Tls-Client-Secret exists")
        if Config.TLS_PROXY_SECRET in request.headers["Tls-Client-Secret"]:
            logger.debug("Tls-Client-Secret is correct")
            if "Tls-Client-Verify" in request.headers.keys():
                logger.debug("Tls-Client-Verify exists")
                if "SUCCESS" in request.headers["Tls-Client-Verify"]:
                    logger.debug("Tls-Client-Verify is correct")
                    if "Tls-Client-Dn" in request.headers.keys():
                        logger.debug("Tls-Client-Dn exists")
                        if session:
                            logger.debug("Session exists")
                            if "user_id" in session.keys():
                                logger.debug("User ID exists")
                                user_id = session["user_id"]
                                new_link = Links(
                                    user_id=int(user_id),
                                    provider_user_id=request.headers["Tls-Client-Dn"],
                                    provider="esteid"
                                )
                                try:
                                    db.session.add(new_link)
                                    db.session.commit()
                                except Exception as e:
                                    logger.debug("Error adding link")
                                    db.session.rollback()
                                    db.session.commit()
                                    sentry.captureException(e)
                                    return render_template("error.html",
                                                           sentry_enabled=True,
                                                           sentAddedry_ask_feedback=True,
                                                           sentry_event_id=g.sentry_event_id,
                                                           sentry_public_dsn=sentry.client.get_public_dsn("https"),
                                                           message=_("Error!"),
                                                           title=_("Error"))
                                return render_template("success.html",
                                                       action=_("Linked"),
                                                       link="./notes",
                                                       title=_("Linked"))
                            else:
                                logger.debug("User ID doesn't exist")
                                try:
                                    user_id = Links.query.filter(
                                        Links.provider_user_id == request.headers["Tls-Client-Dn"]).first()
                                    if user_id is not None:
                                        user_id = user_id.user_id
                                    else:
                                        return render_template("error.html",
                                                               sentry_enabled=True,
                                                               sentry_ask_feedback=True,
                                                               sentry_event_id=g.sentry_event_id,
                                                               sentry_public_dsn=sentry.client.get_public_dsn("https"),
                                                               message=_("Error!"),
                                                               title=_("Error"))
                                    login_user(User.query.get(user_id))
                                    return render_template("success.html",
                                                           action=_("Logged in"),
                                                           link="./notes",
                                                           title=_("Logged in"))
                                except Exception as e:
                                    sentry.captureException(e)
                                    logger.debug("Error loging user in")
                                    return render_template("error.html",
                                                           sentry_enabled=True,
                                                           sentry_ask_feedback=True,
                                                           sentry_event_id=g.sentry_event_id,
                                                           sentry_public_dsn=sentry.client.get_public_dsn("https"),
                                                           message=_("Error!"),
                                                           title=_("Error"))
                        else:
                            try:
                                logger.debug("User ID doesn't exist")
                                user_id = Links.query.filter(
                                    Links.provider_user_id == request.headers["Tls-Client-Dn"]).first()
                                if user_id is not None:
                                    user_id = user_id.user_id
                                else:
                                    logger.debug("User with the link doesn't exist")
                                    return render_template("error.html",
                                                           sentry_enabled=True,
                                                           sentry_ask_feedback=True,
                                                           sentry_event_id=g.sentry_event_id,
                                                           sentry_public_dsn=sentry.client.get_public_dsn("https"),
                                                           message=_("Error!"),
                                                           title=_("Error"))
                                login_user(User.query.get(user_id))
                                return render_template("success.html",
                                                       action=_("Added"),
                                                       link="./notes",
                                                       title=_("Added"))
                            except Exception as e:
                                logger.debug("Exception when trying to log user in")
                                sentry.captureException(e)
                                return render_template("error.html",
                                                       sentry_enabled=True,
                                                       sentry_ask_feedback=True,
                                                       sentry_event_id=g.sentry_event_id,
                                                       sentry_public_dsn=sentry.client.get_public_dsn("https"),
                                                       message=_("Error!"),
                                                       title=_("Error"))
    logger.debug("Check failed")
    return render_template("error.html",
                           sentry_enabled=True,
                           sentry_ask_feedback=True,
                           sentry_event_id=g.sentry_event_id,
                           sentry_public_dsn=sentry.client.get_public_dsn("https"),
                           message=_("Error!"),
                           title=_("Error"))
