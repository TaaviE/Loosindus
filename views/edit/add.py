# coding=utf-8
"""
Routes to create new things
"""
from flask import render_template, url_for
from flask_babelex import gettext as _
from flask_login import login_required

from views.edit.blueprint import edit_page


@edit_page.route("/note", methods=["GET"])
@login_required
def createnote():
    """
    :return: Displays the form required to add a note
    """
    return render_template("creatething.html",
                           action="ADD",
                           confirm=False,
                           endpoint=url_for("edit_page.note_add_new"),
                           row_count=3,
                           label=_("Your wish"),
                           placeholder="")
