"""
app.security
============

Define app's security functionality.
"""
import functools
from typing import Any, Callable

from flask import g, redirect, url_for
from werkzeug import Response


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    """Handle views that require a user be signed in.

    User needs to be logged in to create, edit, and delete posts.

    The new function checks if a user is loaded and redirects to the
    login page otherwise. If a user is loaded the original view is
    called and continues normally.

    :param view:    View function to wrap.
    :return:        The wrapped function supplied to this decorator.
    """

    @functools.wraps(view)
    def _wrapped_view(*args: Any, **kwargs: Any) -> Response:
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return _wrapped_view
