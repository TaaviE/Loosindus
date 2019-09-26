# coding=utf-8
# Copyright: Taavi Eomäe 2017-2019
# SPDX-License-Identifier: AGPL-3.0-only
"""
Contains views that allow testing some specific functionality
"""
from logging import getLogger

from flask import Blueprint, render_template
from flask_babelex import gettext as _
from flask_login import login_required
from flask_mail import Message

from config import Config
from views.static import error_500

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()

test_page = Blueprint("test_page",
                      __name__,
                      template_folder="templates")


@test_page.route("/testerror/<err>", defaults={"err": "404"})
@login_required
def test_err(err):
    """
    Returns the specific error code's error
    """
    return error_500(err)


@test_page.route("/testmail")
@login_required
def test_mail():
    """
    Allows testing mail sending to self
    """
    from main import mail
    with mail.connect() as conn:
        logger.info("Mail verify: {}".format(conn.configure_host().vrfy))
        msg = Message(recipients=["root@localhost"],
                      body="test",
                      subject="test2")

        conn.send(msg)
    return render_template("utility/success.html",
                           action=_("Sent"),
                           link="./testmail",
                           title=_("Sent"))
