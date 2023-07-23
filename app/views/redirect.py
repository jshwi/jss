"""
app.views.redirect
===================
"""
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, url_for

# noinspection PyProtectedMember
from flask_babel import _
from flask_login import current_user, login_required
from itsdangerous import BadSignature
from werkzeug import Response

from app.models import User, db
from app.views.forms import EmptyForm
from app.views.mail import send_email
from app.views.security import (
    confirm_token,
    confirmation_required,
    generate_confirmation_token,
)

blueprint = Blueprint("redirect", __name__, url_prefix="/redirect")


@blueprint.route("/<token>", methods=["GET"])
@login_required
def confirm_email(token: str) -> Response:
    """Confirm each individual user registering with their email.

    There is no view for this route and so the user will be redirected
    to the index page.

    :param token: Encrypted token to verify correct user.
    :return: Response object redirect to index view.
    """
    try:
        email = confirm_token(token)
        user = User.query.filter_by(email=email).first()
        if user.confirmed:
            flash(_("Account already confirmed. Please login."))
        else:
            user.confirmed = True
            user.confirmed_on = datetime.now()
            db.session.add(user)
            db.session.commit()
            flash(_("Your account has been verified."))

    except BadSignature:
        flash(_("The confirmation link is invalid or has expired."))

    return redirect(url_for("index"))


@blueprint.route("/resend", methods=["GET"])
@login_required
def resend_confirmation() -> Response:
    """Resend verification email.

    There is no view for this route and so the user will be redirected
    to the auth/unconfirmed view.

    :return: Response object redirect to auth/unconfirmed view.
    """
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
    flash(_("A new confirmation email has been sent."))
    return redirect(url_for("auth.unconfirmed"))


@blueprint.route("/follow/<username>", methods=["POST"])
@login_required
@confirmation_required
def follow(username: str) -> Response:
    """Add a user model to follow to the current user model.

    There is no view for this route and so the user will be redirected
    to the profile view.

    :param username: User to follow.
    :return: Response object redirect to profile view of user that has
        been followed.
    """
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first_or_404()
        current_user.follow(user)
        db.session.commit()
        flash(_("You are now following %(username)s", username=username))

    return redirect(url_for("public.profile", username=username))


@blueprint.route("/unfollow/<username>", methods=["POST"])
@login_required
@confirmation_required
def unfollow(username: str) -> Response:
    """Remove a user model to unfollow from the current user model.

    There is no view for this route and so the user will be redirected
    to the profile view.

    :param username: User to unfollow.
    :return: response object redirect to profile view of user that has
        been unfollowed.
    """
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first_or_404()
        current_user.unfollow(user)
        db.session.commit()
        flash(_("You are no longer following %(username)s", username=username))

    return redirect(url_for("public.profile", username=username))
