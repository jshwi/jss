"""
app.routes.auth
===============
"""
from __future__ import annotations

from flask import Blueprint, flash, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from jwt import InvalidTokenError
from werkzeug import Response

from app.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
)
from app.models import User, db
from app.utils import redirect
from app.utils.mail import send_email
from app.utils.security import (
    generate_confirmation_token,
    generate_reset_password_token,
    get_requested_reset_password_user,
)
from app.utils.user import create_user

blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@blueprint.route("/register", methods=["GET", "POST"])
def register() -> str | Response:
    """Register a new user account.

    When the user visits the /auth/register URL the register view will
    return an HTML template str with a form for the user to fill out.
    When the user submits the form it will validate their input and
    either create the new user and go to login page or show the form
    again with an error message.

    :return: Rendered register template on GET, or POST with error.
        Response object redirect to the "login" view on successful POST.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = create_user(
            form.username.data, form.email.data, form.password.data
        )
        login_user(user)
        send_email(
            subject="Please verify your email address",
            recipients=[current_user.email],
            html=render_template(
                "email/activate.html",
                confirm_url=url_for(
                    "redirect.confirm_email",
                    token=generate_confirmation_token(current_user.email),
                    _external=True,
                ),
            ),
        )
        flash("A confirmation email has been sent.")
        return redirect.Auth.unconfirmed()

    return render_template("auth/register.html", form=form)


@blueprint.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    """Log in to an existing account.

    The user is queried first and stored in a variable for use later
    use.

    The ``check_password_hash`` function hashes the submitted password
    in the same way as the stored hash and securely compares the two. If
    they match the password is valid.

    The ``session`` object is a dict that stores data across requests.
    When validation succeeds the user ID is stored in a new session.
    The data is then stored in a cookie that is sent to the browser and
    the browser then sends it back with subsequent requests. ``Flask``
    securely signs the data so that it cannot be tampered with.

    At the beginning of each request if a user is logged in their
    information should be loaded and made available to other views.

    :return: Rendered login template on GET or failed login POST.
        Response object redirect to index view on successful login POST.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            if current_user.confirmed:
                return redirect.index()

            flash("You have not verified your account.")
            return redirect.Auth.unconfirmed()

        flash("Invalid username or password.")

    return render_template("auth/login.html", form=form)


@blueprint.route("/logout", methods=["GET"])
def logout() -> Response:
    """Log user out.

    To log out the user's ID needs to be removed from the session.

    The ``load_logged_in_user`` function will not load a user on
    subsequent requests.

    There is no view for this route so user will be redirected the user
    to the index view.

    :return: Response object redirect to index view.
    """
    logout_user()
    return redirect.index()


@blueprint.route("/unconfirmed", methods=["GET"])
@login_required
def unconfirmed() -> str:
    """Unconfirmed email route.

    :return: Rendered auth/unconfirmed template.
    """
    return render_template("auth/unconfirmed.html")


@blueprint.route("/request_password_reset", methods=["GET", "POST"])
def request_password_reset() -> str | Response:
    """Allow user to reset their password.

    Once the request password form is filled in with the user's email
    (if the email address is in the database) send an email with a link
    that leads to the reset password page.

    :return: Rendered auth/request_password_reset template on GET or
        invalid email POST. Response object redirect to "login" view on
        successful email POST.
    """
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("An account with that email address doesn't exist.")
        else:
            send_email(
                subject="Password reset",
                recipients=[user.email],
                html=render_template(
                    "email/reset_password.html",
                    username=user.username,
                    token=generate_reset_password_token(user.id),
                ),
            )
            flash(
                "Please check your inbox for instructions on how to reset "
                "your password"
            )
            return redirect.Auth.login()

    return render_template("auth/request_password_reset.html", form=form)


@blueprint.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token: str) -> str | Response:
    """This route contains the token securely sent to the user's inbox.

    When the token is decrypted, it will return the user's email address
    (if it is valid), and the correct user will be retrieved from the
    database to complete the password reset.

    :param token: Unique token generated from user's email address.
    :return: Rendered auth/reset_password template on GET or invalid
        token POST. Response object redirect to index view on successful
        token POST.
    """
    form = ResetPasswordForm()
    try:
        # error can be raised here for a bad token...
        user = get_requested_reset_password_user(token)

        # ...or here if the token is redundant
        if current_user.is_authenticated:
            raise InvalidTokenError

    except InvalidTokenError:
        flash("The confirmation link is invalid or has expired.")
        return redirect.index()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset.")
        return redirect.Auth.login()

    return render_template("auth/reset_password.html", form=form)
