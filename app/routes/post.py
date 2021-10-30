"""
app.routes.post
===============
"""
from datetime import datetime
from typing import Union

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from werkzeug import Response

from app.utils import redirect
from app.utils.forms import PostForm
from app.utils.models import Post, db
from app.utils.security import authorization_required

blueprint = Blueprint("post", __name__, url_prefix="/post")


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

    return render_template("post/create.html", form=form)


@blueprint.route("/<int:id>", methods=["GET", "POST"])
def read(id: int) -> Union[str, Response]:
    """Render post page for selected post ID.

    :param id: ID of post to display full page on.
    :return: Rendered post template.
    """
    revision = request.args.get("revision", -1, type=int)
    post = Post.get_post(id, revision, checkauthor=False)
    return render_template("post/read.html", post=post, revision=revision)


@blueprint.route("/<int:id>/update/", methods=["GET", "POST"])
@login_required
@authorization_required
def update(id: int) -> Union[str, Response]:
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
        return redirect.index()

    return render_template("post/update.html", post=post, form=form)
