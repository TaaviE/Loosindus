# coding=utf-8
"""
Routes to edit groups
"""
from logging import getLogger

import sentry_sdk
from flask import render_template, request, url_for
from flask_babelex import gettext as _
from flask_login import login_required
from sqlalchemy import and_

from config import Config
from main import db
from models.family_model import Group, GroupAdmin
from models.users_model import User
from utility_standalone import get_user_id
from views.edit.blueprint import edit_page

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()


@edit_page.route("/group/add", methods=["GET"])
@login_required
def add_group():
    """
    Allows creating a single empty group with the given name
    """
    return render_template("creatething.html",
                           row_count=1,
                           endpoint=url_for("edit_page.add_group_post"),
                           label=_("Group name"))


@edit_page.route("/group/<group_id>/removefamily/<family_id>", methods=["GET"])
@login_required
def group_remove_fam(group_id: str, family_id: str):
    """
    Displays a page for removing a family from a group
    """
    # TODO: display confirmation
    try:
        group_id = int(group_id)
        family_id = int(family_id)
    except ValueError:
        logger.warning("Invalid value provided for group_id")
        return render_template("utility/error.html",
                               message=_("An error has occured"),
                               title=_("Error"))
    except Exception as e:
        logger.error(e)
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_("An error has occured"),
                               title=_("Error"))

    return render_template("creatething.html",
                           row_count=1,
                           endpoint=url_for("edit_page.add_group_post"),
                           label=_("Group name"))


@edit_page.route("/group/add", methods=["POST"])
@login_required
def add_group_post():
    """
    Creates a group with the given name
    """
    if "textfield" not in request.form.keys():
        return render_template("utility/error.html",
                               message=_("No form content"),
                               title=_("Error"))

    group_name = request.form["textfield"]

    group = Group(group_name=group_name)

    try:
        db.session.add(group)
        db.session.commit()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.error("Failed adding group")
        return render_template("utility/error.html",
                               message=_("Error adding"),
                               title=_("Error"))

    group_admin = GroupAdmin(group_id=group.id, user_id=get_user_id(), confirmed=True)

    try:
        db.session.add(group_admin)
        db.session.commit()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.error("Failed setting user as the admin")
        return render_template("utility/error.html",
                               message=_("Error adding"),
                               title=_("Error"))

    return render_template("utility/success.html",
                           action=_("Added"),
                           link=url_for("main_page.groups"),
                           title=_("Added"))


@edit_page.route("/group/<group_id>", methods=["GET"])
@login_required
def group_edit_get(group_id: str):
    """
    Allows the group's admin to edit the group
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
                           is_edit_mode=True,
                           is_group_admin=is_group_admin,
                           families=group.families,
                           group_id=group.id,
                           title=_("Event"))


@edit_page.route("/group/<group_id>", methods=["POST"])  # TODO: Maybe merge with editgroup
@login_required
def group_edit(group_id: str):
    """
    :param group_id: The Group ID that is being edited
    """
    user_id = get_user_id()

    try:
        group_id = int(group_id)
    except ValueError:
        logger.warning("Invalid value provided for group_id")
        return render_template("utility/error.html",
                               message=_("An error has occured"),
                               title=_("Error"))
    except Exception as e:
        logger.error(e)
        sentry_sdk.capture_exception(e)
        return render_template("utility/error.html",
                               message=_("An error has occured"),
                               title=_("Error"))

    authorized = False  # Not every user should be able to edit a group
    for admin in GroupAdmin.query.filter(GroupAdmin.group_id == group_id).all():
        if admin.user_id == user_id:
            authorized = True
            break

    if not authorized:
        return render_template("utility/error.html",
                               message=_("Not authorized"),
                               title=_("Error"))

    endpoint = url_for("edit_page.group_edit", group_id=group_id)

    if "action" not in request.form.keys():
        return render_template("utility/error.html",
                               message=_("An error has occured"),
                               title=_("Error"))

    if "confirm" not in request.form.keys():
        if request.form["action"] == "DELETEGROUP":
            # Group deletion is requested but action is not confirmed
            return render_template("creatething.html",
                                   action="DELETEGROUP",
                                   endpoint=endpoint,
                                   id=group_id,
                                   confirm=True)
        elif request.form["action"] == "ADDFAMILY":
            # If family is being added to the group but hasn't been confirmed
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
        elif request.form["action"] == "REMOVEFAM":
            # When family is requested to be removed from a group
            if "extra_data" in request.form.keys():
                extra_data = request.form["extra_data"]
            else:
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))
            return render_template("creatething.html",
                                   action="REMOVEFAM",
                                   endpoint=endpoint,
                                   extra_data=extra_data,
                                   id=group_id,
                                   confirm=True)
    elif request.form["confirm"] == "True":  # The key might have other values
        if request.form["action"] == "DELETEGROUP":
            # If group deletion is requested and confirmed
            try:
                GroupAdmin.query.filter(GroupAdmin.group_id == group_id).delete()
                Group.query.filter(Group.id == group_id).delete()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.warning(e)
                return render_template("utility/error.html",
                                       message=_("Failed deleting group "
                                                 "make sure you delete all the group's events, members and shuffles"),
                                       title=_("Error"))

            return render_template("utility/success.html",
                                   action=_("Deleted"),
                                   link="/",
                                   title=_("Deleted"))
        elif request.form["action"] == "ADDFAMILY":
            # If adding family to group is confirmed
            # TODO: Add user to family
            return render_template("utility/success.html",
                                   action=_("Added"),
                                   link="/",
                                   title=_("Added"))
        elif request.form["action"] == "REMOVEFAM":
            # When family is being removed from a group
            family_id = int(request.form["extra_data"])
            group_id = int(group_id)
            authorized = False
            admin: User  # TODO: Remove when PyCharm's PY-41122 is fixed
            for admin in Group.query.get(group_id).admins:
                if admin.id == user_id:
                    authorized = True
                    break
            if not authorized:
                logger.warning("User {} is trying to forge requests".format(user_id))
                return render_template("utility/error.html",
                                       message=_("An error has occured"),
                                       title=_("Error"))
            target_relationship = GroupAdmin.query.filter(and_(GroupAdmin.group_id == group_id,
                                                               GroupAdmin.family_id == family_id)).one()

            if target_relationship.creator:
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
    else:
        return render_template("utility/error.html",
                               message=_("An error has occured"),
                               title=_("Error"))

    logger.warning("Invalid action POSTed to group edit page")
    return render_template("utility/error.html",
                           message=_("An error has occured"),
                           title=_("Error"))
