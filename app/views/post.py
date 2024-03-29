"""
app.views.post
===============
"""

from __future__ import annotations

import typing as t
from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug import Response

from app.extensions import sitemap
from app.models import Post, db
from app.views.forms import PostForm
from app.views.security import authorization_required

blueprint = Blueprint("post", __name__, url_prefix="/post")


@blueprint.route("/create", methods=["GET", "POST"])
@login_required
@authorization_required
def create() -> str | Response:
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
        # noinspection PyArgumentList
        post = Post(
            title=form.title.data, body=form.body.data, user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("post/create.html", form=form)


@blueprint.route("/<int:id>", methods=["GET", "POST"])
def read(id: int) -> str | Response:
    """Render post page for selected post ID.

    :param id: ID of post to display full page on.
    :return: Rendered post template.
    """
    revision = request.args.get("revision", -1, type=int)
    post = Post.get_post(id, revision, checkauthor=False)
    return render_template("post/read.html", post=post, revision=revision)


@sitemap.register_generator
def sitemap_read() -> (
    t.Generator[tuple[str, dict[str, t.Any], datetime, str, float], None, None]
):
    """Generate post URLs for sitemap.

    :return: Generator yielding data for sitemap.
    """
    posts = Post.query.all()
    for post in posts:
        yield (
            "post.read",
            {"id": post.id},
            datetime.now(),
            current_app.config["SITEMAP_CHANGEFREQ"],
            0.7,
        )


@blueprint.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
@authorization_required
def update(id: int) -> str | Response:
    """Update post that corresponds to the provided post ID.

    :param id: The post's ID.
    :return: Rendered update template on GET or failed POST. Response
        object redirect to index view on successful update POST.
    """
    revision = request.args.get("revision", -1, type=int)
    post = Post.get_post(id, revision)
    form = PostForm(title=post.title, body=post.body)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.edited = datetime.utcnow()
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("post/update.html", post=post, form=form)


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
    return redirect(url_for("index"))
