# coding=utf-8
# Copyright: Taavi Eomäe 2017-2020
# SPDX-License-Identifier: AGPL-3.0-only
"""
Contains views that are related to login
"""
from logging import getLogger
from secrets import token_bytes

import sentry_sdk
from flask import Blueprint, flash, request, session, url_for
from flask_babelex import gettext as _
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.google import make_google_blueprint
from flask_login import current_user, login_required
from flask_security import hash_password, login_user, logout_user
from flask_security.utils import verify_password
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import redirect

from config import Config
from main import app, db
from models.users_model import AuthLinks, User
from utility_standalone import get_id_code, get_sha3_512_hash

login_page = Blueprint("login_page",
                       __name__,
                       template_folder="templates")

getLogger().setLevel(Config.LOGLEVEL)
logger = getLogger()


@login_page.route("/logout")
@login_required
def logout():
    """
    Logs the user out
    """
    logout_user()
    return redirect("/")


@login_page.route("/api/login", methods=["POST"])
def api_login():
    """
    Allows login without CSRF protection if one knows the API key
    """
    username = ""
    try:
        email = request.form["email"]  # TODO: Use header
        password = request.form["password"]
        apikey = request.headers["X-API-Key"]
        if apikey != Config.PRIVATE_API_KEY:
            return "{\"error\": \"error\"}", {"content-type": "text/json"}

        user = User.query.filter(User.email == email).first()

        if verify_password(password, user.password):
            login_user(user)
        else:
            return "{\"error\": \"error\"}", {"content-type": "text/json"}

        return redirect("/")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.info("API login failed for user {}".format(username))
        return "{\"error\": \"error\"}", {"content-type": "text/json"}


if Config.GOOGLE_OAUTH:
    google_blueprint = make_google_blueprint(
        scope=[
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
        ],
        client_id=Config.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=Config.GOOGLE_OAUTH_CLIENT_SECRET,
        redirect_url="https://" + Config.SERVER_NAME + "/"
    )
    google_blueprint.backend = SQLAlchemyStorage(AuthLinks, db.session, user=current_user)
    app.register_blueprint(google_blueprint, url_prefix="/google")


    @oauth_authorized.connect_via(google_blueprint)
    def google_oauth_handler(blueprint, token):
        """
        Passes the oauth event to the oauth handler
        """
        return oauth_handler(blueprint, token)


    @login_page.route("/googleregister")
    def google_signup():
        """
        Sets the required session variable to enable signup when logging in
        """
        session["oauth_sign_up"] = True
        return redirect(url_for("google.login"))


    @login_page.route("/googlelogin")
    def google_login():
        """
        Allows someone to just log in with the OAuth provider
        """
        session["oauth_sign_up"] = False
        return redirect(url_for("google.login"))

if Config.GITHUB_OAUTH:
    github_blueprint = make_github_blueprint(
        scope=["user:email"],
        client_id=Config.GITHUB_OAUTH_CLIENT_ID,
        client_secret=Config.GITHUB_OAUTH_CLIENT_SECRET,
        redirect_url="https://" + Config.SERVER_NAME + "/"
    )
    github_blueprint.backend = SQLAlchemyStorage(AuthLinks, db.session, user=current_user)
    app.register_blueprint(github_blueprint, url_prefix="/github")


    @oauth_authorized.connect_via(github_blueprint)
    def github_oauth_handler(blueprint, token):
        """
        Passes the oauth event to the oauth handler
        """
        return oauth_handler(blueprint, token)


    @login_page.route("/githublogin")
    def github_login():
        """
        Allows someone to just log in with the OAuth provider
        """
        session["oauth_sign_up"] = False
        return redirect(url_for("github.login"))


    @login_page.route("/githubregister")
    def github_signup():
        """
        Sets the required session variable to enable signup when logging in
        """
        session["oauth_sign_up"] = True
        return redirect(url_for("github.login"))

if Config.FACEBOOK_OAUTH:
    facebook_blueprint = make_facebook_blueprint(
        scope=["email"],
        client_id=Config.FACEBOOK_OAUTH_CLIENT_ID,
        client_secret=Config.FACEBOOK_OAUTH_CLIENT_SECRET,
        redirect_url="https://" + Config.SERVER_NAME + "/"
    )
    facebook_blueprint.backend = SQLAlchemyStorage(AuthLinks, db.session, user=current_user)
    app.register_blueprint(facebook_blueprint, url_prefix="/facebook")


    @oauth_authorized.connect_via(facebook_blueprint)
    def facebook_oauth_handler(blueprint, token):
        """
        Passes the oauth event to the oauth handler
        """
        return oauth_handler(blueprint, token)


    @login_page.route("/facebookregister")
    def facebook_signup():
        """
        Sets the required session variable to enable signup when logging in
        """
        session["oauth_sign_up"] = True
        return redirect(url_for("facebook.login"))


    @login_page.route("/facebooklogin")
    def facebook_login():
        """
        Allows someone to just log in with the OAuth provider
        """
        session["oauth_sign_up"] = False
        return redirect(url_for("facebook.login"))


def oauth_handler(blueprint, token):
    """
    Handles incoming OAuth events, login, signup

    :param blueprint:
    :param token:
    :return:
    """
    if token is None:  # Failed
        logger.info("Failed to log in with {}.".format(blueprint.name))
        flash(_("Error logging in"))
        return False

    try:
        if blueprint.name == "github":
            response = blueprint.session.get("/user")
        elif blueprint.name == "google":
            response = blueprint.session.get("/plus/v1/people/me")
        elif blueprint.name == "facebook":
            response = blueprint.session.get("/me?fields=email")
        else:
            logger.critical("Missing blueprint handler for {}".format(blueprint.name))
            flash(_("Error logging in"))
            return False
    except ValueError as e:
        sentry_sdk.capture_exception(e)
        flash(_("Error logging in"))
        return False

    if not response.ok:  # Failed
        logger.info("Failed to fetch user info from {}.".format(blueprint.name))
        logger.info(response)
        flash(_("Error logging in"))
        return False

    response = response.json()
    oauth_user_id = response["id"]  # Get user ID

    try:  # Check if existing service link
        authentication_link = AuthLinks.query.filter_by(
            provider=blueprint.name,
            provider_user_id=str(oauth_user_id),
        ).one()
    except NoResultFound:  # New service link, at least store the token
        authentication_link = AuthLinks(
            provider=blueprint.name,
            provider_user_id=str(oauth_user_id),
            token=token["access_token"],
        )
        logger.info("User not found, keeping token in memory")
    except Exception as e:  # Failure in query!
        sentry_sdk.capture_exception(e)
        logger.error("Failed querying authentication links")
        flash(_("That account is not linked to any system account, check if you already have an account."))
        return False

    # Link exists and it is associated with an user
    if authentication_link is not None and authentication_link.user_id is not None:
        login_user(User.query.get(authentication_link.user_id))
        db.session.commit()
        logger.info("Successfully signed in with {}.".format(blueprint.name))
        return False
    elif authentication_link is not None and \
            authentication_link.user_id is None and \
            "user_id" in session.keys():
        try:
            authentication_link.user_id = int(session["user_id"])  # Update link with user id
            db.session.add(authentication_link)
            db.session.commit()
            return False
        except Exception as e:
            db.session.rollback()
            sentry_sdk.capture_exception(e)
            logger.error("Could not store user and oauth link")
            flash(_("Error signing up, please try again"))
            return False
    else:  # Link does not exist or not associated
        if "oauth_sign_up" in session.keys() and \
                session["oauth_sign_up"]:  # If registration

            session["oauth_sign_up"] = False
            if "email" in response.keys():
                user_email = response["email"]
            else:
                if "emails" in response.keys() and len(response["emails"]) > 0:
                    user_email = response["emails"][0]["value"]
                else:
                    user_email = None

            if "name" in response.keys():
                if blueprint.name == "google":
                    if "givenName" in response["name"].keys():
                        user_name = response["name"]["givenName"]
                    else:
                        logger.info("Google user does not have a givenName")
                        flash(_("Error signing up"))
                        return False
                else:
                    user_name = response["name"]
            else:
                logger.info("User does not have a name!")
                flash(_("Error signing up"))
                return False

            if user_email is None or \
                    len(user_email) < len("a@b.cc") or \
                    "@" not in user_email:  # I'll assume noone with their own TLD will use this
                logger.info("User email is wrong or missing, trying other API endpoint")
                try:
                    if blueprint.name == "github":  # If we're authenticating against GitHub then we have to do
                        # another get
                        response = blueprint.session.get("/user/emails")
                        if not response.ok:
                            flash(_("Error signing up"))
                            logger.info("Error requesting email addresses")
                            return False
                        else:
                            response = response.json()
                            if len(response) > 0 and "email" in response[0].keys():
                                user_email = response[0]["email"]
                            else:
                                user_email = None

                            # Take the first email
                            if not response[0]["verified"] or \
                                    user_email is None or \
                                    len(user_email) < len("a@b.cc") or \
                                    "@" not in user_email:
                                flash(_(
                                    "You have no associated email addresses with your account or none of them are valid"))
                                logger.error("User does not have any emails or none of them are valid")
                                return False
                            else:
                                pass  # All is okay again
                            pass  # New email is fine
                    else:
                        logger.info("No email addresses associated with the account")
                        flash(_("You have no associated email addresses with that account"))
                        return False
                except Exception:
                    logger.info("Error asking for another emails")
                    flash(_("Error signing up"))
                    return False
            else:
                pass  # Email is okay

            try:  # Check if existing service link
                User.query.filter(User.email == user_email).one()
                flash(_("This email address is in use, you must log in with your password to link {provider}"
                        .format(provider=blueprint.name)))
                logger.debug("Email address is in use, but not linked, to avoid hijacks the user must login")
                return False
            except NoResultFound:  # Do not allow same email to sign up again
                pass

            user = User(
                email=user_email,
                username=user_name,
                password=hash_password(token_bytes(100)),
                active=True
            )
            flash(_("Password is set randomly, use \"Forgot password\" to set another password"))

            try:
                db.session.add(user)  # Populate User's ID first by committing
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                sentry_sdk.capture_exception(e)
                logger.error("Could not store user and oauth link")
                flash(_("Error signing up"))
                return False

            try:
                authentication_link.user_id = user.id  # Update link with user id
                db.session.add(authentication_link)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                sentry_sdk.capture_exception(e)
                logger.error("Could not store user and oauth link")
                flash(_("Error signing up"))
                return False

            login_user(user)
            db.session.commit()
            logger.info("Successfully signed up with {}.".format(blueprint.name))
            return False
        else:
            logger.debug("User does not wish to sign up")
            flash(_("You do not have an account"))
            return False


@login_page.route("/clientcert")
def log_user_in_with_cert():
    """
    This functionality requires another subdomain requiring client cert

    Nginx configuration for TLC client certificate authentication (Estonian ID card authentication)
    ```
    proxy_set_header Tls-Client-Secret Config.TLS_PROXY_SECRET;
    proxy_set_header Tls-Client-Verify $ssl_client_verify;
    proxy_set_header Tls-Client-Dn     $ssl_client_s_dn;
    proxy_set_header Tls-Client-Cert   $ssl_client_cert;
    ```
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
                                hashed_dn = get_sha3_512_hash(get_id_code(request.headers["Tls-Client-Dn"]))
                                link = AuthLinks.query.filter(and_(AuthLinks.provider_user_id == hashed_dn,
                                                                   AuthLinks.provider == "esteid")).first()

                                if link is not None:
                                    return redirect("/")

                                link = session["user_id"]
                                new_link = AuthLinks(
                                    user_id=int(link),
                                    provider_user_id=hashed_dn,
                                    token=None,
                                    provider="esteid"
                                )
                                try:
                                    db.session.add(new_link)
                                    db.session.commit()
                                except Exception as e:
                                    logger.debug("Error adding link")
                                    db.session.rollback()
                                    db.session.commit()
                                    sentry_sdk.capture_exception(e)
                                    return redirect(
                                        url_for("static_page.error_page") + "?message=" + _("Error!") + "&title=" + _(
                                            "Error"))
                                return redirect("/")
                            else:
                                logger.debug("User ID doesn't exist")
                                return try_to_log_in_with_dn(request.headers["Tls-Client-Dn"])
                        else:
                            return try_to_log_in_with_dn(request.headers["Tls-Client-Dn"])
    logger.debug("Check failed")
    return redirect(url_for("static_page.error_page") + "?message=" + _("Error!") + "&title=" + _("Error"))


def try_to_log_in_with_dn(input_dn: str) -> object:
    """
    This function allows people to log in based on the hash of the DN of their certificate
    Assumes certificate validity, which also means that the issuing CA has been checked and whitelisted
    Most likely a new ID-card requires new link to be made to log in
    This is a tradeoff unless someone wants to start to store Personal Identification Numbers and parse DNs

    :param input_dn: The DN field of the client certificate
    :return: Returns a redirect depending on result
    """
    try:
        hashed_dn = get_sha3_512_hash(get_id_code(input_dn))
        link = AuthLinks.query.filter(and_(AuthLinks.provider_user_id == hashed_dn,
                                           AuthLinks.provider == "esteid")).first()
        if link is not None:
            user_id = link.user_id
        else:
            hashed_dn = get_sha3_512_hash(input_dn)  # Legacy hashing
            link = AuthLinks.query.filter(and_(AuthLinks.provider_user_id == hashed_dn,
                                               AuthLinks.provider == "esteid")).first()
            if not link:
                logger.debug("User with the link doesn't exist")
                return redirect(url_for("static_page.error_page") + "?message=" + _("Error!") + "&title=" + _("Error"))
            else:
                user_id = link.user_id

        login_user(User.query.get(user_id))
        return redirect(url_for("static_page.success_page") + "?message=" + _("Added!") + "&action=" +
                        _("Added") + "&link=" + "notes" + "&title=" + _("Added"))
    except Exception as e:
        logger.debug("Exception when trying to log user in")
        sentry_sdk.capture_exception(e)
        return redirect(url_for("static_page.error_page") + "?message=" + _("Error!") + "&title=" + _("Error"))
