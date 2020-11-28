# coding=utf-8
# Copyright: Taavi Eomäe 2018-2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Routes to edit families
"""
from logging import getLogger

import sentry_sdk
from flask import render_template, request, url_for
from flask_accept import accept
from flask_babelex import gettext as _
from flask_login import login_required
from sqlalchemy import and_

from config import Config
from main import db
from models.family_model import Family, FamilyAdmin
from models.users_model import User, UserFamily
from utility import commit_object, get_user
from utility_standalone import get_user_id, valid_uuid
from views.edit.blueprint import edit_page

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()


@edit_page.route("/family/add", methods=["POST"])
@login_required
def add_family_post():
    # TODO:
    return ""


@edit_page.route("/family/add", methods=["GET"])
@login_required
def add_family():
    return render_template("creatething.html",
                           row_count=1,
                           endpoint=url_for("edit_page.add_family_post"),
                           label=_("Group ID"))


@edit_page.route("/family/<family_id>", methods=["GET"])
@login_required
def family_edit(family_id: str):
    """
    :param family_id: The family to modify
    """
    user_id = get_user_id()

    try:
        family_id = int(family_id)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_("Broken link"),
                               no_sidebar=not current_user.is_authenticated,
                               title=_("Error"))

    db_family_members = UserFamily.query.filter(UserFamily.family_id == family_id).all()

    family = []
    authorized = False
    for member in db_family_members:
        is_admin = False
        is_person = False
        if member.user_id == user_id:
            is_person = True
            if member.admin:
                authorized = True

        if member.admin:
            is_admin = True

        birthday = None
        try:
            birthday = str(User.query.filter(User.id == member.user_id).first().birthday.strftime("%d.%m"))
        except Exception:
            pass

        family.append(
            (User.query.get(member.user_id).first_name, member.user_id, is_admin, is_person, birthday))

    if not authorized:
        return render_template("utility/error.html",
                               message=_("Not authorized"),
                               title=_("Error"))

    return render_template("editfam.html",
                           family=family,
                           title=_("Edit family"),
                           admin=authorized,
                           family_id=family_id)


@edit_page.route("/family/<family_id>", methods=["POST"])
@login_required
def family_edit_post(family_id: str):
    """
    Deals with all the possible modifications to a family
    """
    family_id = int(family_id)
    endpoint = url_for("edit_page.family_edit_post", family_id=family_id)

    user = get_user()
    admin_families: List[FamilyAdmin] = FamilyAdmin.query.filter(and_(FamilyAdmin.user_id == user.id,
                                                                      FamilyAdmin.family_id == family_id)).first()
    if not admin_families:
        return render_template("utility/error.html",
                               message=_("Not authorized"),
                               title=_("Error"))

    if "action" not in request.form.keys():
        return render_template("utility/error.html",
                               message=_("An error has occured"),
                               title=_("Error"))
    else:
        if request.form["action"] == "REMOVEMEMBER" and "confirm" not in request.form.keys():
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
            target_id = int(request.form["id"])

            admin_relationship = UserFamily.query.filter(and_(UserFamily.user_id == user_id,
                                                              UserFamily.family_id == family_id)).one()

            if not admin_relationship.admin:
                logger.warning(f"User {user.id} is trying to forge requests")
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            target_relationship: UserFamily = UserFamily.query.filter(and_(UserFamily.user_id == target_id,
                                                                           UserFamily.family_id == family_id))
            # TODO: Check if user is admin in family
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
                                   link="/",
                                   title=_("Deleted"))
        elif request.form["action"] == "ADDMEMBER" and "confirm" not in request.form.keys():
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
                                   confirm=True)
        elif request.form["action"] == "ADDMEMBER" and request.form["confirm"] == "True":
            target_id = int(request.form["id"])

            admin_relationship = UserFamily.query.filter(and_(UserFamily.user_id == user_id,
                                                              UserFamily.family_id == family_id)).one()

            if not admin_relationship.admin:
                logger.warning("User {} is trying to forge requests".format(user_id))
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))

            target_relationship = UserFamily()
            target_relationship.user_id = target_id
            target_relationship.admin = False
            target_relationship.family_id = family_id

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
                                   link="/",
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

            admin_relationship = UserFamily.query.filter(and_(UserFamily.user_id == user_id,
                                                              UserFamily.family_id == target_id)).one()

            if not admin_relationship.admin:
                logger.warning("User {user.id} is trying to forge requests")
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
                                   link="/",
                                   title=_("Deleted"))
        else:
            return render_template("utility/error.html",
                                   message=_("An error has occured"),
                                   title=_("Error"))
