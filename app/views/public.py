"""
app.views.public
================
"""
from __future__ import annotations

from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug import Response

from app.models import Post, User
from app.views.forms import EmptyForm

blueprint = Blueprint("public", __name__)


@blueprint.route("/", methods=["GET", "POST"])
def index() -> str:
    """App's index page.

    The index will show all the posts with the most recent first.

    ``JOIN`` is used so that the author information from the user table
    is available in the result.

    :return: Rendered index template.
    """
    page = request.args.get("page", 1, type=int)
    # noinspection PyUnresolvedReferences
    query = Post.query.order_by(Post.created.desc())
    posts = query.paginate(
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    return render_template(
        "public/index.html",
        posts=posts.items,
        next_url=(
            url_for("index", page=posts.next_num) if posts.has_next else None
        ),
        prev_url=(
            url_for("index", page=posts.prev_num) if posts.has_prev else None
        ),
    )


@blueprint.route("/profile/<username>", methods=["GET", "POST"])
def profile(username: str) -> str | Response:
    """Render user's profile page.

    :param username: Username of registered user.
    :return: Rendered profile template.
    """
    user = User.resolve_all_names(username=username)
    if user.username != username:
        return redirect(url_for("public.profile", username=user.username))

    form = EmptyForm()
    user = User.query.filter_by(username=username).first()
    page = request.args.get("page", 1, type=int)
    # noinspection PyUnresolvedReferences
    query = user.posts.order_by(Post.created.desc())
    posts = query.paginate(
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    return render_template(
        "public/profile.html",
        posts=posts.items,
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


@blueprint.route("/favicon.ico")
def favicon() -> Response:
    """Endpoint for the app's favicon.

    :return: Response object.
    """
    path = Path(current_app.root_path) / "static" / "uploads" / "favicon.ico"
    return send_from_directory(
        path.parent if path.is_file() else path.parent.parent,
        path.name,
        mimetype="image/vnd.microsoft.icon",
    )
