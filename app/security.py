"""
app.security
============

Define app's security functionality.
"""
import functools
from time import time
from typing import Any, Callable, Union

import jwt
from flask import current_app, redirect, url_for
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer
from werkzeug import Response

from .extensions import login_manager
from .models import User


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


def confirmation_required(view: Callable[..., Any]) -> Callable[..., Any]:
    """Handle views that require a verified logged in user.

    The new function checks if a user if confirmed or not and redirects
    The user to the auth/unconfirmed page otherwise. If a confirmed user
    is loaded the original view is called and continues normally.

    :param view:    View function to wrap.
    :return:        The wrapped function supplied to this decorator.
    """

    @functools.wraps(view)
    def _wrapped_view(*args: Any, **kwargs: Any) -> Union[str, Response]:
        if not current_user.confirmed:
            return redirect(url_for("auth.unconfirmed"))

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


def generate_reset_password_token(user_id: int, max_age: int = 600) -> str:
    """Generate a hashed token leading to the reset password route.

    :param user_id: The ID of the user requesting a password reset.
    :param max_age: The maximum time the token is valid for.
    :return:        A unique token hashed from user's ID.
    """
    return jwt.encode(
        {"reset_password": user_id, "exp": time() + max_age},
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )


def get_requested_reset_password_user(token: str) -> User:
    """Decode the user's token and return the user model.

    :param token:   Token to decrypt.
    :return:        User, if the token is valid, else None.
    """
    id = jwt.decode(
        token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
    )["reset_password"]
    return User.query.get(id)
