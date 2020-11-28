# coding=utf-8
# Copyright: Taavi Eomäe 2017-2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Contains all of the routes that aren't really super specific to Loosindus
"""
from logging import getLogger

from flask import Blueprint, render_template, request, send_from_directory
from flask_babelex import gettext as _
from flask_login import current_user
from flask_security import login_required

from config import Config
from main import app
from views.views import index

static_page = Blueprint("static_page",
                        __name__,
                        template_folder="templates")

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()


# Show a friendlier error page
@app.errorhandler(500)
@app.errorhandler(404)
@app.errorhandler(405)
def error_500(err):
    """
    Displays the nice error handling page
    """

    logger.info(str(err))
    if "404" in str(err):
        message = _("Unfortunately this page was not found")
        logger.debug(f"Route for URL {request.url} was not found")
    else:
        message = _("An error occured")

    return render_template("utility/error.html",
                           no_video=True,
                           message=message,
                           title=_("Error"))


# Views
@static_page.route("/test")
@login_required
def test():
    """
    Displays a the error page for testing
    """
    return render_template("utility/error.html",
                           message=_("Here you go!"),
                           title=_("Error"))


@static_page.route("/favicon.ico")
def favicon():
    """
    Returns the site's favicon
    """
    return send_from_directory("./static",
                               "favicon-16x16.png")


@static_page.route("/feedback")
@login_required
def feedback():
    """
    Allows submitting feedback about the application
    """
    return render_template("feedback.html",
                           sentry_feedback=True)


@static_page.route("/about")
def about():
    """
    Displays a nice introductory page
    """
    return render_template("generic/pretty_index.html", title="Loosindus")


@static_page.route("/")
def home():
    """
    Displays a home page based on user logon status
    """
    if current_user.is_authenticated:
        return index()
    else:
        return about()


@static_page.route("/contact", methods=["GET"])
def contact():
    """
    Displays a contact details page
    """

    return render_template("generic/contact.html",
                           no_sidebar=not current_user.is_authenticated)


@static_page.route("/help", methods=["GET"])
def help_page():
    """
    :return: A help page
    """
    return render_template("generic/help.html")


@static_page.route("/error")
def error_page():
    """
    Displays an error page
    """
    message = _("Broken link")
    title = _("Error")

    try:
        title = request.args["title"]
        message = request.args["message"]
    except Exception:
        pass

    return render_template("utility/error.html",
                           message=message,
                           no_video=True,
                           no_sidebar=not current_user.is_authenticated,
                           title=title)


@static_page.route("/tos")
def terms_of_service():
    """
    Displays terms of service
    """
    return render_template("generic/terms_of_service.html",
                           no_sidebar=not current_user.is_authenticated,
                           title=_("Terms of Service"))


@static_page.route("/pp")
def privacy_policy():
    """
    Displays the service's privacy policy
    """

    return render_template("generic/privacy_policy.html",
                           title=_("Privacy Policy"),
                           no_sidebar=not current_user.is_authenticated)


@static_page.route("/success")
def success_page():
    """
    Displays a success page based on given parameters
    """
    message = _("Broken link")
    title = _("Error")
    action = ""
    link = ""

    try:
        title = request.args["title"]
        message = request.args["message"]
        action = request.args["action"]
        link = request.args["link"]  # TODO: Check if for this domain only
    except Exception:
        pass

    return render_template("utility/success.html",
                           message=message,
                           action=(action if action != "" else title),
                           link=link,
                           no_sidebar=not current_user.is_authenticated,
                           title=title)


@static_page.route("/ads.txt", methods=["GET"])
def ads_txt():
    """
    Displays ads.txt
    """
    return render_template("generic/ads.txt"), {"content-type": "text/plain"}


@static_page.route("/sitemap.xml", methods=["GET"])
def sitemap():
    """
    Displays the software's sitemap
    """
    return render_template("generic/sitemap.xml"), {"content-type": "text/xml"}


@static_page.route("/robots.txt", methods=["GET"])
def robots():
    """
    Displays the standard robots.txt
    """
    return render_template("generic/robots.txt"), {"content-type": "text/plain"}
