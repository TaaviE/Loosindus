# coding=utf-8
# Copyright: Taavi Eomäe 2017-2019
# SPDX-License-Identifier: AGPL-3.0-only
"""
Contains all of the routes that display an edit or
"""
from logging import getLogger

import sentry_sdk
from flask import Blueprint, redirect, render_template, request, session
from flask_babelex import gettext as _
from flask_login import current_user, login_required

from config import Config
from main import db
from models.users_model import User, UserFamilyAdmin
from models.wishlist_model import Wishlist, wishlist_status_to_id

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()

edit_page = Blueprint("edit_page",
                      __name__,
                      url_prefix="edit",
                      template_folder="templates")


@edit_page.route("/note", methods=["GET"])
@login_required
def createnote():
    """
    :return: Displays the form required to add a note
    """
    return render_template("creatething.html",
                           action="ADD",
                           confirm=False,
                           endpoint="createnote",
                           row_count=3,
                           label=_("Your wish"),
                           placeholder="")


@edit_page.route("/note/<request_id>", methods=["GET"])
@login_required
def editnote(request_id: str):
    """
    Displays a page where a person can edit a note
    """
    user_id = int(session["user_id"])
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
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_("An error occured"),
                               title=_("Error"))

    return render_template("creatething.html",
                           action="ADD",
                           confirm=False,
                           endpoint="editnote",
                           row_count=3,
                           extra_data=request.args["id"],
                           label=_("Your wish"),
                           placeholder=db_note.item)


@edit_page.route("/note", methods=["POST"])
@login_required
def editnote_edit():
    """
    Allows submitting textual edits to notes
    """
    user_id = session["user_id"]
    logger.debug("Got a post request to edit a note by user id: {}".format(user_id))

    addednote = request.form["textfield"]
    try:
        request_id = request.form["extra_data"]
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
                           link="./notes",
                           title=_("Changed"))


@edit_page.route("/removenote", methods=["POST"])
@login_required
def deletenote():
    """
    Allows deleting a specific note
    """
    user_id = int(session["user_id"])
    user = User.query.get(user_id)
    username = user.first_name

    if "confirm" not in request.form.keys():
        return render_template("creatething.html",
                               action="DELETE",
                               endpoint="removenote",
                               extra_data=request.form["extra_data"],
                               confirm=True)

    try:
        request_id = request.form["extra_data"]
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
                               message=_("Can't find what you wanted to delete"),
                               title=_("Error"))

    logger.info("Removed {} note with ID {}".format(username, request_id))
    return render_template("utility/success.html",
                           action=_("Removed"),
                           link="./notes",
                           title=_("Removed"))


@edit_page.route("/note", methods=["POST"])
@login_required
def createnote_add():
    """
    Allows submitting new notes to a wishlist
    """
    logger.debug("Got a post request to add a note")
    user_id = int(session["user_id"])
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
        #    with open("./notes/" + useridno, "r") as file:
        #        currentnotes = json.load(file)
        db_notes = Wishlist.query.filter(Wishlist.user_id == user_id).all()
        for note in db_notes:
            currentnotes[note.item] = note.id
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise e

    if len(currentnotes) >= 200:
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
        sentry_sdk.capture_exception(e)
        raise e

    return render_template("utility/success.html",
                           action=_("Added"),
                           link="./notes",
                           title=_("Added"))


@edit_page.route("/editfam/<family_id>", methods=["GET"])
@login_required
def editfamily(family_id: str):
    """
    :param family_id: The family to modify
    """
    user_id = int(session["user_id"])

    try:
        family_id = int(family_id)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_("Broken link"),
                               no_sidebar=not current_user.is_authenticated,
                               title=_("Error"))

    db_family_members = UserFamilyAdmin.query.filter(
        UserFamilyAdmin.family_id == family_id).all()

    family = []
    show_admin_column = False
    for member in db_family_members:
        is_admin = False
        is_person = False
        if member.user_id == user_id:
            is_person = True
            if member.admin:
                show_admin_column = True

        if member.admin:
            is_admin = True

        birthday = None
        try:
            birthday = str(User.query.filter(User.id == member.user_id).first().birthday.strftime("%d.%m"))
        except Exception:
            pass

        family.append(
            (User.query.get(member.user_id).first_name, member.user_id, is_admin, is_person, birthday))

    return render_template("editfam.html",
                           family=family,
                           title=_("Edit family"),
                           admin=show_admin_column,
                           family_id=family_id)


@edit_page.route("/setlanguage", methods=["POST"])
@login_required
def set_language():
    """
    Allows the user to set their language
    """
    user_id = session["user_id"]
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
                               link="./notes",
                               title=_("Added"))
    except Exception:
        # No need to capture with Sentry, someone's just meddling
        return render_template("utility/error.html",
                               message=_("Faulty input"),
                               title=_("Error"))


@edit_page.route("/editgroup", methods=["GET"])
@login_required
def editgroup():
    user_id = session["user_id"]
    # user_obj = User.query.get(user_id)

    try:
        group_id = request.args["id"]
        group_id = int(group_id)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_("Faulty input"),
                               title=_("Error"))

    db_families_in_group = get_families_in_group(group_id)

    families = []
    for family in db_families_in_group:
        families.append((family.name, family.id))

    is_admin = False
    if if_user_is_group_admin(group_id, user_id):
        is_admin = True

    return render_template("editgroup.html",
                           title=_("Edit group"),
                           families=families,
                           group_id=request.args["id"],
                           admin=is_admin)


@edit_page.route("/editgroup", methods=["POST"])  # TODO: Maybe merge with editgroup
@login_required
def editgroup_with_action():
    user_id = int(session["user_id"])
    endpoint = "editgroup"
    if "action" not in request.form.keys():
        return render_template("utility/error.html",
                               message=_("An error has occured"),
                               title=_("Error"))
    else:
        if request.form["action"] == "REMOVEFAM" and "confirm" not in request.form.keys():
            if "extra_data" in request.form.keys():
                extra_data = request.form["extra_data"]
            else:
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            if "id" in request.form.keys():
                form_id = request.form["id"]
            else:
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            return render_template("creatething.html",
                                   action="REMOVEFAM",
                                   endpoint=endpoint,
                                   extra_data=extra_data,
                                   id=form_id,
                                   confirm=True)
        elif request.form["action"] == "REMOVEFAM" and request.form["confirm"] == "True":
            family_id = int(request.form["extra_data"])
            group_id = int(request.form["id"])

            admin_relationship = UserGroupAdmin.query.filter(and_(UserGroupAdmin.group_id == group_id,
                                                                  UserGroupAdmin.user_id == user_id)).one()

            if not admin_relationship.admin:
                logger.warning("User {} is trying to forge requests".format(user_id))
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            target_relationship = FamilyGroup.query.filter(and_(FamilyGroup.group_id == group_id,
                                                                FamilyGroup.family_id == family_id)).one()

            if target_relationship.admin:
                return render_template("utility/error.html",
                                       message=_("You can not delete an admin from your family"),
                                       title=_("Error"))

            target_relationship.delete()

            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            return render_template("utility/success.html",
                                   action=_("Deleted"),
                                   link="./",
                                   title=_("Deleted"))
        elif request.form["action"] == "ADDFAMILY" and "confirm" not in request.form.keys():
            if "extra_data" in request.form.keys():
                extra_data = request.form["extra_data"]
            else:
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            if "id" in request.form.keys():
                form_id = request.form["id"]
            else:
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            return render_template("creatething.html",
                                   action="ADDFAMILY",
                                   endpoint=endpoint,
                                   extra_data=extra_data,
                                   id=form_id,
                                   confirm=True)
        elif request.form["action"] == "ADDFAMILY" and request.form["confirm"] == "True":
            # TODO: Add user to family
            return render_template("utility/success.html",
                                   action=_("Added"),
                                   link="./",
                                   title=_("Added"))
        elif request.form["action"] == "DELETEGROUP" and "confirm" not in request.form.keys():
            if "extra_data" in request.form.keys():
                extra_data = request.form["extra_data"]
            else:
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            if "id" in request.form.keys():
                form_id = request.form["id"]
            else:
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            return render_template("creatething.html",
                                   action="DELETEGROUP",
                                   endpoint=endpoint,
                                   id=form_id,
                                   extra_data=extra_data,
                                   confirm=True)
        elif request.form["action"] == "DELETEGROUP" and request.form["confirm"] == "True":
            # TODO: Delete group
            return render_template("utility/success.html",
                                   action=_("Deleted"),
                                   link="./",
                                   title=_("Deleted"))
        else:
            return render_template("utility/error.html",
                                   message=_("An error has occured"),
                                   title=_("Error"))


@edit_page.route("/editfam", methods=["POST"])
@login_required
def editfam_with_action():
    """
    Deals with all the possible modifications to a family
    """
    user_id = int(session["user_id"])
    endpoint = "editfam"
    if "action" not in request.form.keys():
        return render_template("utility/error.html",
                               message=_("An error has occured"),
                               title=_("Error"))
    else:
        if request.form["action"] == "REMOVEMEMBER" and "confirm" not in request.form.keys():
            if "extra_data" in request.form.keys():
                extra_data = request.form["extra_data"]
            else:
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            if "id" in request.form.keys():
                form_id = request.form["id"]
            else:
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            return render_template("creatething.html",
                                   action="REMOVEMEMBER",
                                   endpoint=endpoint,
                                   id=form_id,
                                   extra_data=extra_data,
                                   confirm=True)
        elif request.form["action"] == "REMOVEMEMBER" and request.form["confirm"] == "True":
            family_id = int(request.form["extra_data"])
            target_id = int(request.form["id"])

            admin_relationship = UserFamilyAdmin.query.filter(and_(UserFamilyAdmin.user_id == user_id,
                                                                   UserFamilyAdmin.family_id == family_id)).one()

            if not admin_relationship.admin:
                logger.warning("User {} is trying to forge requests".format(user_id))
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            target_relationship = UserFamilyAdmin.query.filter(and_(UserFamilyAdmin.user_id == target_id,
                                                                    UserFamilyAdmin.family_id == family_id))

            if target_relationship.admin:
                return render_template("utility/error.html",
                                       message=_("You can not delete an admin from your family"),
                                       title=_("Error"))

            target_relationship.delete()

            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            return render_template("utility/success.html",
                                   action=_("Deleted"),
                                   link="./",
                                   title=_("Deleted"))
        elif request.form["action"] == "ADDMEMBER" and "confirm" not in request.form.keys():
            if "extra_data" in request.form.keys():
                extra_data = request.form["extra_data"]
            else:
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            if "id" in request.form.keys():
                form_id = request.form["id"]
            else:
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            return render_template("creatething.html",
                                   action="ADDMEMBER",
                                   endpoint=endpoint,
                                   id=form_id,
                                   extra_data=extra_data,
                                   confirm=True)
        elif request.form["action"] == "ADDMEMBER" and request.form["confirm"] == "True":
            family_id = int(request.form["extra_data"])
            target_id = int(request.form["id"])

            admin_relationship = UserFamilyAdmin.query.filter(and_(UserFamilyAdmin.user_id == user_id,
                                                                   UserFamilyAdmin.family_id == family_id)).one()

            if not admin_relationship.admin:
                logger.warning("User {} is trying to forge requests".format(user_id))
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            target_relationship = UserFamilyAdmin(user_id=target_id,
                                                  admin=False,
                                                  family_id=family_id)

            try:
                db.session.add(target_relationship)
                db.session.commit()
            except Exception:
                db.session.rollback()
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))
            return render_template("utility/success.html",
                                   action=_("Added"),
                                   link="./",
                                   title=_("Added"))
        elif request.form["action"] == "DELETEFAM" and "confirm" not in request.form.keys():
            if "extra_data" in request.form.keys():
                extra_data = request.form["extra_data"]
            else:
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            if "id" in request.form.keys():
                form_id = request.form["id"]
            else:
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            return render_template("creatething.html",
                                   action="DELETEFAM",
                                   endpoint=endpoint,
                                   id=form_id,
                                   extra_data=extra_data,
                                   confirm=True)
        elif request.form["action"] == "DELETEFAM" and request.form["confirm"] == "True":
            target_id = int(request.form["id"])

            admin_relationship = UserFamilyAdmin.query.filter(and_(UserFamilyAdmin.user_id == user_id,
                                                                   UserFamilyAdmin.family_id == target_id)).one()

            if not admin_relationship.admin:
                logger.warning("User {} is trying to forge requests".format(user_id))
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            Family.query.filter(and_(Family.id == target_id)).one().delete()

            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))
            return render_template("utility/success.html",
                                   action=_("Deleted"),
                                   link="./",
                                   title=_("Deleted"))
        else:
            return render_template("utility/error.html",
                                   message=_("An error has occured"),
                                   title=_("Error"))


@edit_page.route("/addfam", methods=["GET"])
@login_required
def add_family():
    return render_template("creatething.html",
                           row_count=1,
                           endpoint="editfam",
                           label=_("Group ID"))


@edit_page.route("/addgroup", methods=["GET"])
@login_required
def add_group():
    return render_template("creatething.html",
                           row_count=1,
                           endpoint="editgroup",
                           label=_("Group ID"))


@edit_page.route("/recreategraph", methods=["GET"])
@login_required
def ask_regraph():
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


@edit_page.route("/recreategraph", methods=["POST"])
@login_required
def regraph():
    user_id = session["user_id"]
    try:
        event_id = int(request.form["extra_data"])
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_("An error has occured"),
                               title=_("Error"))
    family_obj = Family.query.get(family_id)
    time_right_now = datetime.datetime.now()

    database_families = Family.query.filter(
        Family.id.in_(
            set([familygroup.family_id for familygroup in FamilyGroup.query.filter(
                FamilyGroup.family_id == family_obj.id
            ).all()])
        )
    ).all()
    database_all_families_with_members = []
    for db_family in database_families:
        database_family_members = UserFamilyAdmin.query.filter(
            UserFamilyAdmin.family_id == db_family.id).all()
        database_all_families_with_members.append((db_family.id, database_family_members))

    user_id_to_user_number = {}
    user_number_to_user_id = {}
    start_id = 0
    for family_id, db_family in database_all_families_with_members:
        for member in db_family:
            user_number_to_user_id[start_id] = member.user_id
            user_id_to_user_number[member.user_id] = start_id
            start_id += 1

    try:
        if not UserGroupAdmin.query.filter(
                UserGroupAdmin.user_id == int(user_id) and UserGroupAdmin.admin == True).one():
            return render_template("utility/error.html",
                                   message=_("Access denied"),
                                   title=_("Error"))
    except NoResultFound:
        return render_template("utility/error.html",
                               message=_("Access denied"),
                               title=_("Error"))
    except Exception as e:
        sentry_sdk.capture_exception(e)

    families = []
    family_ids_map = {}
    for family_index, (list_family_id, list_family) in enumerate(database_all_families_with_members):
        families.insert(family_index, {})
        for person_index, person in enumerate(list_family):
            family_ids_map[family_index] = list_family_id
            families[family_index][get_person_name(person.user_id)] = user_id_to_user_number[person.user_id]

    families_shuf_ids = {}
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

    last_connections = secretsanta.connectiongraph.ConnectionGraph(members_to_families, families_to_members)

    family_group = FamilyGroup.query.filter(FamilyGroup.family_id == family_obj.id).one().group_id
    for group_shuffle in Shuffle.query.filter(Shuffle.group == family_group).all():  # Get last previous shuffles
        last_connections.add(user_id_to_user_number[group_shuffle.giver],
                             user_id_to_user_number[group_shuffle.getter],
                             group_shuffle.year)

    logger.info("{} is the year of Linux Desktop".format(time_right_now.year))

    santa = secretsanta.secretsantagraph.SecretSantaGraph(families_to_members, members_to_families, last_connections)

    shuffled_ids_str = {}
    for connection in santa.generate_connections(time_right_now.year):
        families_shuf_ids[connection.source] = connection.target
        shuffled_ids_str[str(connection.source)] = str(connection.target)

    logger.info(shuffled_ids_str)

    for giver, getter in families_shuf_ids.items():
        # The assumption is that one group shouldn't have more than one shuffle a year active
        # at the same time, there can be multiple with different years
        db_entry_shuffle = Shuffle(
            giver=user_number_to_user_id[giver],
            getter=user_number_to_user_id[getter],
            year=time_right_now.year,
            group=family_group
        )
        try:
            db.session.add(db_entry_shuffle)
            db.session.commit()
        except Exception:
            db.session.rollback()
            try:
                row = Shuffle.query.filter(and_(Shuffle.giver == user_number_to_user_id[giver],
                                                Shuffle.year == time_right_now.year)).one()
                if row.getter != user_number_to_user_id[getter]:
                    row.getter = user_number_to_user_id[getter]
                    db.session.commit()
            except Exception:
                db.session.rollback()

            sentry_sdk.capture_exception(e)

    return render_template("utility/success.html",
                           action=_("Generated"),
                           link="./notes",
                           title=_("Generated"))


@edit_page.route("/note/<id>", methods=["POST"])
@login_required
def update_note_status(id: str):
    """
    Allows setting specific wishlist note's status
    """
    user_id = int(session["user_id"])

    # TODO: Check if they should be able to change
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
            # then abort (modified only happens after edit of a note)
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

    return redirect("/" + str(id), code=303)
