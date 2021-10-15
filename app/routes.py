"""
app.routes
==========

A view function is written to respond to application requests.

``Flask`` uses patterns to match the incoming request URL to the view
that should handle it. The view returns data that ``Flask`` turns into
an outgoing response.

``Flask`` can also go the other direction and generate a URL to view
based on its name and arguments.
"""
from datetime import datetime
from typing import Optional, Union

from flask import (
    Blueprint,
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from itsdangerous import BadSignature
from jwt import InvalidTokenError
from werkzeug import Response

from .forms import (
    EditProfile,
    EmptyForm,
    LoginForm,
    MessageForm,
    PostForm,
    RegistrationForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
)
from .mail import send_email
from .models import Message, Notification, Post, User, Usernames, db
from .post import render_post_nav_template
from .security import (
    authorization_required,
    confirm_token,
    confirmation_required,
    generate_confirmation_token,
    generate_reset_password_token,
    get_requested_reset_password_user,
)
from .user import create_user

_TEMPLATE_INDEX = "public/index.html"
_URL_FOR_INDEX = "index"
_URL_FOR_UNCONFIRMED = "auth.unconfirmed"
_URL_FOR_PROFILE = "views.profile"

views_blueprint = Blueprint("views", __name__)
auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    """Register a new user account.

    When the user visits the /auth/register URL the register view will
    return an HTML template str with a form for the user to fill out.
    When the user submits the form it will validate their input and
    either create the new user and go to login page or show the form
    again with an error message.

    :return:    Rendered register template on GET, or POST with error.
                Response object redirect to login view on successful
                POST.
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
                    "auth.confirm_email",
                    token=generate_confirmation_token(current_user.email),
                    _external=True,
                ),
            ),
        )
        flash("A confirmation email has been sent.")
        return redirect(url_for(_URL_FOR_UNCONFIRMED))

    return render_template("auth/register.html", form=form)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
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

    :return:    Rendered login template on GET or failed login POST.
                Response object redirect to index view on successful
                login POST.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            if current_user.confirmed:
                return redirect(url_for(_URL_FOR_INDEX))

            flash("You have not verified your account.")
            return redirect(url_for(_URL_FOR_UNCONFIRMED))

        flash("Invalid username or password.")

    return render_template("auth/login.html", form=form)


@auth_blueprint.route("/logout", methods=["GET"])
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
    return redirect(url_for(_URL_FOR_INDEX))


@views_blueprint.route("/", methods=["GET", "POST"])
def index() -> str:
    """App's index page.

    The index will show all of the posts with the most recent first.

    ``JOIN`` is used so that the author information from the user table
    is available in the result.

    :return: Rendered index template.
    """
    return render_post_nav_template(
        Post.query.order_by(Post.created.desc()),
        _TEMPLATE_INDEX,
        _URL_FOR_INDEX,
    )


@views_blueprint.route("/create", methods=["GET", "POST"])
@login_required
@authorization_required
def create() -> Union[str, Response]:
    """Create a post.

    The decorator will ensure that the user is logged in to visit this
    view, otherwise they will be redirected the login page.

    The create view works the same as the auth register view. The posted
    data is validated and either the form is displayed (and the post is
    added to the database) or an error is shown.

    :return:    Rendered create template on GET or failed POST. Response
                object redirect to index view on successful POST.
    """
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data, body=form.body.data, user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for(_URL_FOR_INDEX))

    return render_template("user/create.html", form=form)


@views_blueprint.route("/<int:id>/update/", methods=["GET", "POST"])
@views_blueprint.route(
    "/<int:id>/update/<int:revision>", methods=["GET", "POST"]
)
@login_required
@authorization_required
def update(id: int, revision: Optional[int] = None) -> Union[str, Response]:
    """Update post that corresponds to the provided post ID.

    :param id:          The post's ID.
    :param revision:    Version to revert to.
    :return:            Rendered update template on GET or failed POST.
                        Response object redirect to index view on
                        successful update POST.
    """
    post = Post.get_post(id, revision)
    form = PostForm(title=post.title, body=post.body)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.edited = datetime.utcnow()
        db.session.commit()
        return redirect(url_for(_URL_FOR_INDEX))

    return render_template("user/update.html", post=post, form=form)


@views_blueprint.route("/<int:id>/delete", methods=["POST"])
@login_required
@authorization_required
def delete(id: int) -> Response:
    """Delete post by post's ID.

    The delete view does not have its own template. Since there is no
    template it will only handle the ``POST`` method and then redirect
    to the index view.

    :param id:  The post's ID.
    :return:    Response object redirect to index view.
    """
    post = Post.get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for(_URL_FOR_INDEX))


@auth_blueprint.route("/<token>", methods=["GET"])
@login_required
def confirm_email(token: str) -> Response:
    """Confirm each individual user registering with their email.

    There is no view for this route and so the user will be redirected
    to the index page.

    :param token:   Encrypted token to verify correct user.
    :return:        Response object redirect to index view.
    """
    try:
        email = confirm_token(token)
        user = User.query.filter_by(email=email).first()
        if user.confirmed:
            flash("Account already confirmed. Please login.")
        else:
            user.confirmed = True
            user.confirmed_on = datetime.now()
            db.session.add(user)
            db.session.commit()
            flash("Your account has been verified.")

    except BadSignature:
        flash("The confirmation link is invalid or has expired.")

    return redirect(url_for(_URL_FOR_INDEX))


@auth_blueprint.route("/unconfirmed", methods=["GET"])
@login_required
def unconfirmed() -> str:
    """Unconfirmed email route.

    :return: Rendered auth/unconfirmed template.
    """
    return render_template("auth/unconfirmed.html")


@auth_blueprint.route("/resend", methods=["GET"])
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
                "auth.confirm_email",
                token=generate_confirmation_token(current_user.email),
                _external=True,
            ),
        ),
    )
    flash("A new confirmation email has been sent.")
    return redirect(url_for(_URL_FOR_UNCONFIRMED))


@auth_blueprint.route("/request_password_reset", methods=["GET", "POST"])
def request_password_reset() -> Union[str, Response]:
    """Allow user to reset their password.

    Once the request password form is filled in with the user's email
    (if the email address is in the database) send an email with a link
    that leads to the reset password page.

    :return:        Rendered auth/request_password_reset template on
                    GET or invalid email POST. Response object redirect
                    to login view on successful email POST.
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
            return redirect(url_for("auth.login"))

    return render_template("auth/request_password_reset.html", form=form)


@auth_blueprint.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token: str) -> Union[str, Response]:
    """This route contains the token securely sent to the user's inbox.

    When the token is decrypted, it will return the user's email address
    (if it is valid), and the correct user will be retrieved from the
    database to complete the password reset.

    :param token:   Unique token generated from user's email address.
    :return:        Rendered auth/reset_password template on GET or
                    invalid token POST. Response object redirect to
                    index view on successful token POST.
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
        return redirect(url_for(_URL_FOR_INDEX))

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset.")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form)


@views_blueprint.route("/profile/<username>", methods=["GET", "POST"])
def profile(username: str) -> Union[str, Response]:
    """Render user's profile page.

    :param username:    Username of registered user.
    :return:            Rendered profile template.
    """
    user = User.resolve_all_names(username=username)
    if user.username != username:
        return redirect(url_for(_URL_FOR_PROFILE, username=user.username))

    form = EmptyForm()
    # noinspection PyUnresolvedReferences
    return render_post_nav_template(
        user.posts.order_by(Post.created.desc()),
        "public/profile.html",
        _URL_FOR_PROFILE,
        username=username,
        user=user,
        form=form,
    )


# noinspection PyShadowingBuiltins
@views_blueprint.route("/post/<int:id>", methods=["GET"])
def post_page(id: int) -> str:
    """Render post page for selected post ID.

    :param id:  ID of post to display full page on.
    :return:    Rendered post template.
    """
    post = Post.get_post(id, checkauthor=False)
    return render_template("public/post.html", post=post)


@views_blueprint.before_request
def before_request() -> None:
    """Add user's login date and time before first request."""
    if current_user.is_authenticated:
        current_user.last_seen = (  # pylint: disable=assigning-non-slot
            datetime.now()
        )
        db.session.commit()


@views_blueprint.route("/profile/edit", methods=["GET", "POST"])
@login_required
@confirmation_required
def edit_profile() -> Union[str, Response]:
    """Edit a user's personal profile page.

    :return:    Rendered profile/edit template on GET. Response object
                redirect to index view on successful POST.
    """
    old_username = current_user.username
    form = EditProfile(
        username=current_user.username,  # pylint: disable=assigning-non-slot
        about_me=current_user.about_me,  # pylint: disable=assigning-non-slot
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

        return redirect(
            url_for(_URL_FOR_PROFILE, username=current_user.username)
        )

    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
    return render_template("user/edit_profile.html", form=form)


@views_blueprint.route("/follow/<username>", methods=["POST"])
@login_required
@confirmation_required
def follow(username: str) -> Response:
    """Add a user model to follow to the current user model.

    There is no view for this route and so the user will be redirected
    to the profile view.

    :param username:    User to follow.
    :return:            Response object redirect to profile view of
                        user that has been followed.
    """
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first_or_404()
        current_user.follow(user)
        db.session.commit()
        flash(f"You are now following {username}")

    return redirect(url_for(_URL_FOR_PROFILE, username=username))


@views_blueprint.route("/unfollow/<username>", methods=["POST"])
@login_required
@confirmation_required
def unfollow(username: str) -> Response:
    """Remove a user model to unfollow from the current user model.

    There is no view for this route and so the user will be redirected
    to the profile view.

    :param username:    User to unfollow.
    :return:            response object redirect to profile view of
                        user that has been unfollowed.
    """
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first_or_404()
        current_user.unfollow(user)
        db.session.commit()
        flash(f"You are no longer following {username}")

    return redirect(url_for(_URL_FOR_PROFILE, username=username))


@views_blueprint.route("/send_message/<recipient>", methods=["GET", "POST"])
@login_required
@confirmation_required
def send_message(recipient: str) -> Union[str, Response]:
    """Send IM to another user.

    :return:    Rendered user/send_message template on GET. Response
                object redirect to recipient's view on successful POST.
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
        return redirect(url_for(_URL_FOR_PROFILE, username=recipient))

    return render_template(
        "user/send_message.html", form=form, recipient=recipient
    )


# noinspection PyUnresolvedReferences
@views_blueprint.route("/messages")
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
    return render_post_nav_template(
        current_user.messages_received.order_by(Message.created.desc()),
        "user/messages.html",
        "views.messages",
    )


@views_blueprint.route("/notifications")
@login_required
def notifications() -> Response:
    """Retrieve notifications for logged in user.

    :return: Response containing JSON payload.
    """
    since = request.args.get("since", 0.0, type=float)
    # noinspection PyUnresolvedReferences
    query = current_user.notifications.filter(
        Notification.timestamp > since
    ).order_by(Notification.timestamp.asc())
    return jsonify(
        [
            {"name": q.name, "data": q.get_mapping(), "timestamp": q.timestamp}
            for q in query
        ]
    )


@views_blueprint.route("/export_posts")
@login_required
@confirmation_required
def export_posts() -> Response:
    """Redirect user to /export_posts route which triggers event.

    There is no view for this route and so the user will be redirected
    to the profile view.

    :return:    response object redirect to profile view of user that
                has requested the post export (current user).
    """
    if current_user.get_task_in_progress("export_posts"):
        flash("An export task is already in progress")
    else:
        current_user.launch_task("export_posts", "Exporting posts...")
        db.session.commit()

    return redirect(url_for(_URL_FOR_PROFILE, username=current_user.username))


@views_blueprint.route("/<int:id>/version/<int:revision>")
@login_required
@authorization_required
def version(id: int, revision: int) -> Union[str, Response]:
    """Rewind versioned post that corresponds to the provided post ID.

    :param id:          The post's ID.
    :param revision:    Version to revert to.
    :return:            Rendered update template on GET or failed POST.
                        Response object redirect to index view on
                        successful update POST.
    """
    post = Post.get_post(id, revision)
    form = EmptyForm()
    return render_template(
        "public/post.html", post=post, id=id, revision=revision, form=form
    )


def init_app(app: Flask) -> None:
    """Load the app with views views.

    :param app: App to register blueprints with.
    """
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.strip_trailing_newlines = False
    app.register_blueprint(views_blueprint)
    app.register_blueprint(auth_blueprint)
    app.add_url_rule("/", endpoint=_URL_FOR_INDEX)
