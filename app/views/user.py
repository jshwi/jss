"""
app.views.user
===============
"""
from __future__ import annotations

from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug import Response

from app.models import Message, Notification, User, Usernames, db
from app.views.forms import EditProfile, MessageForm
from app.views.security import confirmation_required

blueprint = Blueprint("user", __name__, url_prefix="/user")


@blueprint.route("/profile/edit", methods=["GET", "POST"])
@login_required
@confirmation_required
def edit_profile() -> str | Response:
    """Edit a user's personal profile page.

    :return: Rendered profile/edit template on GET. Response object
        redirect to index view on successful POST.
    """
    old_username = current_user.username
    form = EditProfile(
        username=current_user.username, about_me=current_user.about_me
    )
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        if old_username != current_user.username:
            usernames = Usernames(
                username=old_username, user_id=current_user.id
            )
            db.session.add(usernames)
            db.session.commit()

        return redirect(
            url_for("public.profile", username=current_user.username)
        )

    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
    return render_template("user/edit_profile.html", form=form)


@blueprint.route("/send_message/<recipient>", methods=["GET", "POST"])
@login_required
@confirmation_required
def send_message(recipient: str) -> str | Response:
    """Send message to another user.

    :param recipient: Email address to send email to.
    :return: Rendered user/send_message template on GET. Response object
        redirect to recipient's view on successful POST.
    """
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            # `author` and `recipient` are backrefs in `User` and are
            # not defined as columns
            author=current_user,  # type: ignore
            recipient=user,  # type: ignore
            body=form.message.data,
        )
        db.session.add(message)
        user.add_notifications("unread_message_count", user.new_messages())
        db.session.commit()
        flash("Your message has been sent.")
        return redirect(url_for("public.profile", username=recipient))

    return render_template(
        "user/send_message.html", form=form, recipient=recipient
    )


@blueprint.route("/messages")
@login_required
@confirmation_required
def messages() -> str:
    """View received messages delivered to logged in user.

    :return: Rendered user/messages template to view received messages.
    """
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notifications("unread_message_count", 0)
    db.session.commit()
    page = request.args.get("page", 1, type=int)
    query = current_user.messages_received.order_by(Message.created.desc())
    posts = query.paginate(page, current_app.config["POSTS_PER_PAGE"], False)
    return render_template(
        "user/messages.html",
        posts=posts.items,
        next_url=(
            url_for("user.messages", page=posts.next_num)
            if posts.has_next
            else None
        ),
        prev_url=(
            url_for("user.messages", page=posts.prev_num)
            if posts.has_prev
            else None
        ),
    )


@blueprint.route("/notifications")
@login_required
def notifications() -> Response:
    """Retrieve notifications for logged-in user.

    :return: Response containing JSON payload.
    """
    since = request.args.get("since", 0.0, type=float)
    query = current_user.notifications.filter(
        Notification.timestamp > since
    ).order_by(Notification.timestamp.asc())
    return jsonify(
        [
            {"name": q.name, "data": q.get_mapping(), "timestamp": q.timestamp}
            for q in query
        ]
    )
