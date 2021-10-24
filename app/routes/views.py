"""
app.routes.views
================
"""
from datetime import datetime
from typing import Optional, Union

from flask import Blueprint, current_app, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug import Response

from app import redirect
from app.forms import EmptyForm, PostForm
from app.models import Post, User, db
from app.security import authorization_required

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
