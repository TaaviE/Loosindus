# coding=utf-8
"""
Contains all of the routes that aren't really super specific to Loosindus
"""
from functools import lru_cache

from flask import g, render_template, request, send_from_directory, session
from flask_security import login_required, logout_user

from views import _, app, current_user, index, logger, main_page, redirect, sentry


# Show a friendlier error page
@app.errorhandler(500)
@app.errorhandler(404)
@app.errorhandler(405)
@main_page.route("/testerror/<err>", defaults={"err": "Testing error"})
def error_500(err):
    """
    Displays the nice error handling page
    """
    message = _("An error occured")
    try:
        if not current_user.is_authenticated:
            sentry_enabled = False
        else:
            sentry_enabled = True
    except Exception:
        sentry_enabled = False

    logger.info(str(err))
    if "404" in str(err):
        message = _("Unfortunately this page was not found")

    return render_template("utility/error.html",
                           sentry_enabled=sentry_enabled,
                           sentry_ask_feedback=True,
                           no_video=True,
                           sentry_event_id=g.sentry_event_id,
                           sentry_public_dsn=sentry.client.get_public_dsn("https"),
                           message=message,
                           title=_("Error"))


# Views
@main_page.route("/test")
@login_required
def test():
    """
    Displays a the error page for testing
    """
    return render_template("utility/error.html",
                           message=_("Here you go!"),
                           title=_("Error"))


@main_page.route("/favicon.ico")
def favicon():
    """
    Returns the site's favicon
    """
    return send_from_directory("./static",
                               "favicon-16x16.png")


@main_page.route("/feedback")
@login_required
def feedback():
    """
    Allows submitting feedback about the application
    """
    return render_template("feedback.html",
                           sentry_feedback=True,
                           sentry_event_id=g.sentry_event_id,
                           sentry_public_dsn=sentry.client.get_public_dsn("https"))


@main_page.route("/about")
def about():
    """
    Displays a nice introductory page
    """
    return render_template("generic/pretty_index.html", title="Loosindus")


@main_page.route("/")
def home():
    """
    Displays a home page based on user logon status
    """
    if current_user.is_authenticated:
        return index()
    else:
        return about()


@main_page.route("/contact")
def contact():
    """
    Displays a contact details page
    """

    return render_template("generic/contact.html",
                           no_sidebar=not current_user.is_authenticated)


@main_page.route("/worker.js")
def worker_js():
    """
    Returns serviceworker JS
    """
    return render_template("worker.js"), 200, {"content-type": "application/javascript"}


@main_page.route("/logout")
@login_required
def logout():
    """
    Logs the user out
    """
    logout_user()
    return redirect("/")


@main_page.route("/help", methods=["GET"])
def help_page():
    """
    :return: A help page
    """
    return render_template("generic/help.html")


@main_page.route("/custom.js")
@login_required
@lru_cache(maxsize=10)
def custom_js():
    """
    User-specific JS for custom functionality
    """
    sentry_feedback = False
    sentry_event_id = ""
    sentry_public_dns = ""

    if "event_id" in request.args.keys():
        sentry_feedback = True
        sentry_event_id = request.args["event_id"]
        sentry_public_dns = request.args["dsn"]

    return render_template("custom.js",
                           sentry_feedback=sentry_feedback,
                           user_id=int(session["user_id"]),
                           sentry_event_id=sentry_event_id,
                           sentry_public_dsn=sentry_public_dns,
                           ), 200, {"content-type": "application/javascript"}


@main_page.route("/error")
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
                           sentry_enabled=True,
                           sentry_ask_feedback=True,
                           sentry_event_id=g.sentry_event_id,
                           sentry_public_dsn=sentry.client.get_public_dsn("https"),
                           message=message,
                           no_video=True,
                           no_sidebar=not current_user.is_authenticated,
                           title=title)


@main_page.route("/tos")
def terms_of_service():
    """
    Displays terms of service
    """
    return render_template("generic/terms_of_service.html",
                           no_sidebar=not current_user.is_authenticated,
                           title=_("Terms of Service"))


@main_page.route("/pp")
def privacy_policy():
    """
    Displays the service's privacy policy
    """

    return render_template("generic/privacy_policy.html",
                           title=_("Privacy Policy"),
                           no_sidebar=not current_user.is_authenticated)


@main_page.route("/success")
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
                           link="./" + link,
                           no_sidebar=not current_user.is_authenticated,
                           title=title)
