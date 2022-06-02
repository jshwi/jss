"""
app.routes.redirect
===================
"""
from datetime import datetime

from flask import Blueprint, flash, render_template, url_for

# noinspection PyProtectedMember
from flask_babel import _
from flask_login import current_user, login_required
from itsdangerous import BadSignature
from werkzeug import Response

from app.forms import EmptyForm
from app.models import Post, User, db
from app.utils import redirect
from app.utils.mail import send_email
from app.utils.security import (
    authorization_required,
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

    return redirect.index()


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
    return redirect.Auth.unconfirmed()


@blueprint.route("/<int:id>/delete", methods=["POST"])
@login_required
@authorization_required
def delete(id: int) -> Response:
    """Delete post by post's ID.

    The "delete" view does not have its own template. Since there is no
    template it will only handle the ``POST`` method and then redirect
    to the index view.

    :param id: The post's ID.
    :return: Response object redirect to index view.
    """
    post = Post.get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect.index()


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

    return redirect.Public.profile(username=username)


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

    return redirect.Public.profile(username=username)


@blueprint.route("/export_posts")
@login_required
@confirmation_required
def export_posts() -> Response:
    """Redirect user to /export_posts route which triggers event.

    There is no view for this route and so the user will be redirected
    to the profile view.

    :return: response object redirect to profile view of user that has
        requested the post export (current user).
    """
    if current_user.get_task_in_progress("export_posts"):
        flash(_("An export task is already in progress"))
    else:
        current_user.launch_task("export_posts", "Exporting posts...")
        db.session.commit()

    return redirect.Public.profile(username=current_user.username)
