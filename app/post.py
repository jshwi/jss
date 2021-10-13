"""
app.post
========

Helper function(s) for user posting.
"""
from typing import Any

from flask import current_app, render_template, request, url_for
from flask_sqlalchemy import BaseQuery


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
