"""
app.post
========

Helper function(s) for user posting.
"""
from sqlite3 import Connection

from flask import g
from werkzeug import exceptions

from .models import get_db


def get_post(id: int, checkauthor: bool = True) -> Connection:
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
    :param checkauthor:    Rule whether to check for author ID.
    :return:                Post's connection object.
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username "
            "FROM post p JOIN user u ON p.author_id = u.id "
            "WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        exceptions.abort(404, f"Post id {id} doesn't exist.")

    if checkauthor and post["author_id"] != g.user["id"]:
        exceptions.abort(403)

    return post
