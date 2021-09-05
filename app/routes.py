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
from typing import Union

from flask import (
    Blueprint,
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug import Response

from .models import Post, User, db
from .post import get_post
from .user import create_user

_URL_FOR_INDEX = "index"

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
    if request.method == "POST":
        error = None
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        if not username:
            error = "Username is required."
        elif not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."
        elif User.query.filter_by(username=username).first() is not None:
            error = f"User {username} is already registered."
        elif User.query.filter_by(email=email).first() is not None:
            error = f"Email {email} is already registered."

        if error is None:
            create_user(username, email, password)
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


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
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("index"))

        flash("Invalid username or password.")

    return render_template("auth/login.html")


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
    if request.method == "POST":
        error = None
        title = request.form["title"]
        body = request.form["body"]

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            post = Post(title=title, body=body, user_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for(_URL_FOR_INDEX))

    return render_template("user/create.html")


@views_blueprint.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
def update(id: int) -> Union[str, Response]:
    """Update post that corresponds to the provided post ID.

    :param id:  The post's ID.
    :return:    Rendered update template on GET or failed POST. Response
                object redirect to index view on successful update POST.
    """
    post = get_post(id)
    if request.method == "POST":
        error = None
        title = request.form["title"]

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            post.title = request.form.get("title")
            post.body = request.form.get("body")
            db.session.commit()
            return redirect(url_for(_URL_FOR_INDEX))

    return render_template("user/update.html", post=post)


@views_blueprint.route("/<int:id>/delete", methods=["POST"])
@login_required
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


def init_app(app: Flask) -> None:
    """Load the app with views views.

    :param app: App to register blueprints with.
    """
    app.register_blueprint(views_blueprint)
    app.register_blueprint(auth_blueprint)
    app.add_url_rule("/", endpoint="index")
