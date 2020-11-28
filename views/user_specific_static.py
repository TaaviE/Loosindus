# coding=utf-8
# Copyright: Taavi Eomäe 2017-2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Contains views that are static for a specific user
"""
from flask import Blueprint, render_template, session
from flask_login import login_required

user_specific = Blueprint("user_specific", __name__, template_folder="templates")


@user_specific.route("/custom.js")
@login_required
def custom_js():
    """
    User-specific JS for custom functionality
    """
    return render_template("custom.js", user_id=int(session["user_id"])), \
           200, \
           {"content-type": "application/javascript"}


@user_specific.route("/worker.js")
@login_required
def worker_js():
    """
    Returns serviceworker JS
    """
    return render_template("worker.js"), \
           200, \
           {"content-type": "application/javascript"}
