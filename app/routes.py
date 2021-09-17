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
from typing import Union

from flask import Blueprint, Flask, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from itsdangerous import BadSignature
from jwt import InvalidTokenError
from werkzeug import Response

from .forms import (
    LoginForm,
    PostForm,
    RegistrationForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
)
from .mail import send_email
from .models import Post, User, db
from .post import get_post
from .security import (
    admin_required,
    confirm_token,
    generate_confirmation_token,
    generate_reset_password_token,
    get_requested_reset_password_user,
)
from .user import create_user

_URL_FOR_INDEX = "index"
_URL_FOR_UNCONFIRMED = "auth.unconfirmed"

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
                return redirect(url_for("index"))

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
    return redirect(url_for("index"))


@views_blueprint.route("/", methods=["GET", "POST"])
def index() -> str:
    """App's index page.

    The index will show all of the posts with the most recent first.

    ``JOIN`` is used so that the author information from the user table
    is available in the result.

    :return: Rendered index template.
    """
    # noinspection PyUnresolvedReferences
    posts = Post.query.order_by(Post.created.desc())
    return render_template("index.html", posts=posts)


@views_blueprint.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
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


@views_blueprint.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
@admin_required
def update(id: int) -> Union[str, Response]:
    """Update post that corresponds to the provided post ID.

    :param id:  The post's ID.
    :return:    Rendered update template on GET or failed POST. Response
                object redirect to index view on successful update POST.
    """
    post = get_post(id)
    form = PostForm(title=post.title, body=post.body)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.commit()
        return redirect(url_for(_URL_FOR_INDEX))

    return render_template("user/update.html", post=post, form=form)


@views_blueprint.route("/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(id: int) -> Response:
    """Delete post by post's ID.

    The delete view does not have its own template. Since there is no
    template it will only handle the ``POST`` method and then redirect
    to the index view.

    :param id:  The post's ID.
    :return:    Response object redirect to index view.
    """
    post = get_post(id)
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

    return redirect(url_for("index"))


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
        return redirect(url_for("index"))

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset.")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form)


@views_blueprint.route("/profile/<username>", methods=["GET", "POST"])
def profile(username: str) -> str:
    """Render user's profile page.

    :param username:    Username of registered user.
    :return:            Rendered profile template.
    """
    user = User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(user_id=user.id)
    return render_template("profile.html", user=user, posts=posts)


# noinspection PyShadowingBuiltins
@views_blueprint.route("/post/<int:id>", methods=["GET"])
def post_page(id: int) -> str:
    """Render post page for selected post ID.

    :param id:  ID of post to display full page on.
    :return:    Rendered post template.
    """
    post = get_post(id, checkauthor=False)
    return render_template("post.html", post=post)


def init_app(app: Flask) -> None:
    """Load the app with views views.

    :param app: App to register blueprints with.
    """
    app.register_blueprint(views_blueprint)
    app.register_blueprint(auth_blueprint)
    app.add_url_rule("/", endpoint="index")
