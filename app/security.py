"""
app.security
============

Define app's security functionality.
"""
import functools
from typing import Any, Callable, Union

from flask import current_app
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer
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


def generate_confirmation_token(email: str) -> Union[str, bytes]:
    """Generate unique token for verifying new user's email.

    :param email:   Email of recipient.
    :return:        Unique token for user to authenticate with.
    """
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(
        email, salt=current_app.config["SECURITY_PASSWORD_SALT"]
    )


def confirm_token(token: str, max_age: int = 3600) -> str:
    """Confirm token for verifying new user's email.

    :param token:   Token to serialize with secret key.
    :param max_age: Max age of token before considered invalid.
    :return:        Return user's email if valid.
    """
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.loads(
        token,
        salt=current_app.config["SECURITY_PASSWORD_SALT"],
        max_age=max_age,
    )
