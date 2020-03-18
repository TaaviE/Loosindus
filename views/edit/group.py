# coding=utf-8
"""
Routes to edit groups
"""
from logging import getLogger

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
    endpoint = url_for("edit_page.editfam_with_action")
    if "action" not in request.form.keys():
        return render_template("utility/error.html",
                               message=_("An error has occured"),
                               title=_("Error"))
    else:
        if request.form["action"] == "REMOVEFAM" and \
                "confirm" not in request.form.keys():
            # When family is requested to be removed from a group
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
        elif request.form["action"] == "REMOVEFAM" and \
                request.form["confirm"] == "True":
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
        elif request.form["action"] == "ADDFAMILY" and \
                "confirm" not in request.form.keys():
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
        elif request.form["action"] == "ADDFAMILY" and \
                request.form["confirm"] == "True":
            # If adding family to group is confirmed
            # TODO: Add user to family
            return render_template("utility/success.html",
                                   action=_("Added"),
                                   link="/",
                                   title=_("Added"))
        elif request.form["action"] == "DELETEGROUP" and \
                "confirm" not in request.form.keys():
            # Group deletion is requested but action is not confirmed
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
        elif request.form["action"] == "DELETEGROUP" and \
                request.form["confirm"] == "True":
            # If group deletion is requested and confirmed
            # TODO: Delete group
            return render_template("utility/success.html",
                                   action=_("Deleted"),
                                   link="/",
                                   title=_("Deleted"))
        else:
            return render_template("utility/error.html",
                                   message=_("An error has occured"),
                                   title=_("Error"))
