"""
app.routes.views
================
"""
from datetime import datetime
from typing import Optional, Union

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug import Response

from app import redirect
from app.forms import EditProfile, EmptyForm, MessageForm, PostForm
from app.models import Message, Notification, Post, User, Usernames, db
from app.security import authorization_required, confirmation_required

blueprint = Blueprint("views", __name__)


# noinspection DuplicatedCode
@blueprint.route("/", methods=["GET", "POST"])
def index() -> str:
    """App's index page.

    The index will show all of the posts with the most recent first.

    ``JOIN`` is used so that the author information from the user table
    is available in the result.

    :return: Rendered index template.
    """
    page = request.args.get("page", 1, type=int)
    query = Post.query.order_by(Post.created.desc())
    posts = query.paginate(page, current_app.config["POSTS_PER_PAGE"], False)
    return render_template(
        "public/index.html",
        posts=posts,
        next_url=(
            url_for("index", page=posts.next_num) if posts.has_next else None
        ),
        prev_url=(
            url_for("index", page=posts.prev_num) if posts.has_prev else None
        ),
    )


@blueprint.route("/create", methods=["GET", "POST"])
@login_required
@authorization_required
def create() -> Union[str, Response]:
    """Create a post.

    The decorator will ensure that the user is logged in to visit this
    view, otherwise they will be redirected the login page.

    The create view works the same as the auth register view. The posted
    data is validated and either the form is displayed (and the post is
    added to the database) or an error is shown.

    :return: Rendered create template on GET or failed POST. Response
        object redirect to index view on successful POST.
    """
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data, body=form.body.data, user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        return redirect.index()

    return render_template("user/create.html", form=form)


@blueprint.route("/<int:id>/update/", methods=["GET", "POST"])
@blueprint.route("/<int:id>/update/<int:revision>", methods=["GET", "POST"])
@login_required
@authorization_required
def update(id: int, revision: Optional[int] = None) -> Union[str, Response]:
    """Update post that corresponds to the provided post ID.

    :param id: The post's ID.
    :param revision: Version to revert to.
    :return: Rendered update template on GET or failed POST. Response
        object redirect to index view on successful update POST.
    """
    post = Post.get_post(id, revision)
    form = PostForm(title=post.title, body=post.body)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.edited = datetime.utcnow()
        db.session.commit()
        return redirect.index()

    return render_template("user/update.html", post=post, form=form)


@blueprint.route("/<int:id>/delete", methods=["POST"])
@login_required
@authorization_required
def delete(id: int) -> Response:
    """Delete post by post's ID.

    The delete view does not have its own template. Since there is no
    template it will only handle the ``POST`` method and then redirect
    to the index view.

    :param id: The post's ID.
    :return: Response object redirect to index view.
    """
    post = Post.get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect.index()


@blueprint.route("/profile/<username>", methods=["GET", "POST"])
def profile(username: str) -> Union[str, Response]:
    """Render user's profile page.

    :param username: Username of registered user.
    :return: Rendered profile template.
    """
    user = User.resolve_all_names(username=username)
    if user.username != username:
        return redirect.Views.profile(username=user.username)

    form = EmptyForm()
    user = User.query.filter_by(username=username).first()
    page = request.args.get("page", 1, type=int)
    query = user.posts.order_by(Post.created.desc())
    posts = query.paginate(page, current_app.config["POSTS_PER_PAGE"], False)
    return render_template(
        "public/profile.html",
        posts=posts,
        username=username,
        user=user,
        form=form,
        next_url=(
            url_for("views.profile", username=username, page=posts.next_num)
            if posts.has_next
            else None
        ),
        prev_url=(
            url_for("views.profile", username=username, page=posts.prev_num)
            if posts.has_prev
            else None
        ),
    )


@blueprint.route("/post/<int:id>", methods=["GET"])
def post_page(id: int) -> str:
    """Render post page for selected post ID.

    :param id: ID of post to display full page on.
    :return: Rendered post template.
    """
    post = Post.get_post(id, checkauthor=False)
    return render_template("public/post.html", post=post)


@blueprint.before_request
def before_request() -> None:
    """Add user's login date and time before first request."""
    if current_user.is_authenticated:
        current_user.last_seen = (  # pylint: disable=assigning-non-slot
            datetime.now()
        )
        db.session.commit()


@blueprint.route("/profile/edit", methods=["GET", "POST"])
@login_required
@confirmation_required
def edit_profile() -> Union[str, Response]:
    """Edit a user's personal profile page.

    :return: Rendered profile/edit template on GET. Response object
        redirect to index view on successful POST.
    """
    old_username = current_user.username
    form = EditProfile(
        username=current_user.username, about_me=current_user.about_me
    )
    if form.validate_on_submit():
        current_user.username = (  # pylint: disable=assigning-non-slot
            form.username.data
        )
        current_user.about_me = (  # pylint: disable=assigning-non-slot
            form.about_me.data
        )
        db.session.commit()
        flash("Your changes have been saved.")
        if old_username != current_user.username:
            usernames = Usernames(
                username=old_username, user_id=current_user.id
            )
            db.session.add(usernames)
            db.session.commit()

        return redirect.Views.profile(username=current_user.username)

    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
    return render_template("user/edit_profile.html", form=form)


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
        flash(f"You are now following {username}")

    return redirect.Views.profile(username=username)


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
        flash(f"You are no longer following {username}")

    return redirect.Views.profile(username=username)


@blueprint.route("/send_message/<recipient>", methods=["GET", "POST"])
@login_required
@confirmation_required
def send_message(recipient: str) -> Union[str, Response]:
    """Send IM to another user.

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
        return redirect.Views.profile(username=recipient)

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
    # pylint: disable=assigning-non-slot
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notifications("unread_message_count", 0)
    db.session.commit()
    page = request.args.get("page", 1, type=int)
    query = current_user.messages_received.order_by(Message.created.desc())
    posts = query.paginate(page, current_app.config["POSTS_PER_PAGE"], False)
    return render_template(
        "user/messages.html",
        posts=posts,
        next_url=(
            url_for("views.messages", page=posts.next_num)
            if posts.has_next
            else None
        ),
        prev_url=(
            url_for("views.messages", page=posts.prev_num)
            if posts.has_prev
            else None
        ),
    )


@blueprint.route("/notifications")
@login_required
def notifications() -> Response:
    """Retrieve notifications for logged in user.

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
        flash("An export task is already in progress")
    else:
        current_user.launch_task("export_posts", "Exporting posts...")
        db.session.commit()

    return redirect.Views.profile(username=current_user.username)


@blueprint.route("/<int:id>/version/<int:revision>")
@login_required
@authorization_required
def version(id: int, revision: int) -> Union[str, Response]:
    """Rewind versioned post that corresponds to the provided post ID.

    :param id: The post's ID.
    :param revision: Version to revert to.
    :return: Rendered update template on GET or failed POST. Response
        object redirect to index view on successful update POST.
    """
    post = Post.get_post(id, revision)
    form = EmptyForm()
    return render_template(
        "public/post.html", post=post, id=id, revision=revision, form=form
    )
