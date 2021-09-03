"""
app.security
============

Define app's security functionality.
"""
import functools
from typing import Any, Callable

from flask_login import current_user
from werkzeug import Response

from .extensions import login_manager


def admin_required(view: Callable[..., Any]) -> Callable[..., Any]:
    """Handle views that require an admin be signed in.

    Admin needs to be logged in to create, edit, and delete posts.

    The new function checks if a admin is loaded and returns a
    ``401 Unauthorized`` error otherwise. If an admin user is loaded the
    original view is called and continues normally.

    :param view:    View function to wrap.
    :return:        The wrapped function supplied to this decorator.
    """

    @functools.wraps(view)
    def _wrapped_view(*args: Any, **kwargs: Any) -> Response:
        if not current_user.admin:
            return login_manager.unauthorized()

        return view(*args, **kwargs)

    return _wrapped_view
