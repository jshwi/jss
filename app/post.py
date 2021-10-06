"""
app.post
========

Helper function(s) for user posting.
"""
from typing import Any, Optional

from flask import abort, current_app, render_template, request, url_for
from flask_login import current_user
from flask_sqlalchemy import BaseQuery

from .models import Post


def get_post(
    id: int, version: Optional[int] = None, checkauthor: bool = True
) -> Post:
    """Get post by post's ID.

    Check if the author matches the logged in user. To keep the code DRY
    this can get the post and call it from each view.

    ``_exceptions.abort`` will raise a special exception that
    returns an HTTP status code. It takes an optional message to show
    with the error, otherwise a default message is used.

        - 404: "Not Found"
        - 403: "Forbidden
        - 401: "Unauthorized"

    This will redirect to the login page instead of returning that
    status.

    The ``checkauthor`` argument is defined so that the function can be
    used to get a post without checking the author. This would be useful
    if we wrote a view to show an individual post on a page where the
    user doesn't matter, because they are not modifying the post.

    :param id:              The post's ID.
    :param version:         If provided populate session object with
                            version.
    :param checkauthor:    Rule whether to check for author ID.
    :return:                Post's connection object.
    """
    post = Post.query.get(id)
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if version is not None:
        try:
            post_version = post.versions[version]
            post.title = post_version.title
            post.body = post_version.body
        except IndexError:
            abort(404)

    if checkauthor and post.user_id != current_user.id:
        abort(403)

    return post


def render_post_nav_template(
    query: BaseQuery, render: str, nav_url_for: str, **kwargs: Any
) -> str:
    """Render a template which can utilise previous and next navigation.

    :param query:       Base query object.
    :param render:      HTML template to render.
    :param nav_url_for: Dot separated function reference.
    :param kwargs:      Additional kwargs to render template.
    :return:            Rendered template.
    """
    page = request.args.get("page", 1, type=int)
    posts = query.paginate(page, current_app.config["POSTS_PER_PAGE"], False)
    next_url = (
        url_for(nav_url_for, page=posts.next_num, **kwargs)
        if posts.has_next
        else None
    )
    prev_url = (
        url_for(nav_url_for, page=posts.prev_num, **kwargs)
        if posts.has_prev
        else None
    )
    return render_template(
        render,
        next_url=next_url,
        prev_url=prev_url,
        posts=posts.items,
        **kwargs,
    )
