"""
app.routes.views
================
"""
from typing import Union

from flask import Blueprint, current_app, render_template, request, url_for
from werkzeug import Response

from app.utils import redirect
from app.utils.forms import EmptyForm
from app.utils.models import Post, User

blueprint = Blueprint("public", __name__)


# noinspection DuplicatedCode
@blueprint.route("/", methods=["GET", "POST"])
def index() -> str:
    """App's index page.

    The index will show all the posts with the most recent first.

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


@blueprint.route("/profile/<username>", methods=["GET", "POST"])
def profile(username: str) -> Union[str, Response]:
    """Render user's profile page.

    :param username: Username of registered user.
    :return: Rendered profile template.
    """
    user = User.resolve_all_names(username=username)
    if user.username != username:
        return redirect.Public.profile(username=user.username)

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
            url_for("public.profile", username=username, page=posts.next_num)
            if posts.has_next
            else None
        ),
        prev_url=(
            url_for("public.profile", username=username, page=posts.prev_num)
            if posts.has_prev
            else None
        ),
    )
