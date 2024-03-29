"""
app.views.security
==================

Define app's security functionality.
"""

from __future__ import annotations

import functools
import typing as t
from time import time

import jwt
from flask import current_app, redirect, url_for
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer
from werkzeug import Response

from app.extensions import login_manager
from app.models import User


def admin_required(
    view: t.Callable[..., str | Response]
) -> t.Callable[..., str | Response]:
    """Handle views that require an admin be signed in.

    Admin needs to be logged in to create, edit, and delete posts.

    The new function checks if an admin is loaded and returns a
    ``401 Unauthorized`` error otherwise. If an admin user is loaded the
    original view is called and continues normally.

    :param view: View function to wrap.
    :return: The wrapped function supplied to this decorator.
    """

    @functools.wraps(view)
    def _wrapped_view(*args: object, **kwargs: object) -> str | Response:
        if not current_user.admin:
            return login_manager.unauthorized()

        return view(*args, **kwargs)

    return _wrapped_view


def authorization_required(
    view: t.Callable[..., str | Response]
) -> t.Callable[..., str | Response]:
    """Handle views that require an authorized user be signed in.

    The new function checks if an authorized user is loaded and returns
    a ``401 Unauthorized`` error otherwise. If an authorized user is
    loaded the original view is called and continues normally.

    :param view: View function to wrap.
    :return: The wrapped function supplied to this decorator.
    """

    @functools.wraps(view)
    def _wrapped_view(*args: object, **kwargs: object) -> str | Response:
        if not current_user.authorized:
            return login_manager.unauthorized()

        return view(*args, **kwargs)

    return _wrapped_view


def confirmation_required(
    view: t.Callable[..., str | Response]
) -> t.Callable[..., str | Response]:
    """Handle views that require a verified logged-in user.

    The new function checks if a user is confirmed or not and redirects
    The user to the auth/unconfirmed page otherwise. If a confirmed user
    is loaded the original view is called and continues normally.

    :param view: View function to wrap.
    :return: The wrapped function supplied to this decorator.
    """

    @functools.wraps(view)
    def _wrapped_view(*args: t.Any, **kwargs: t.Any) -> str | Response:
        if not current_user.confirmed:
            return redirect(url_for("auth.unconfirmed"))

        return view(*args, **kwargs)

    return _wrapped_view


def generate_confirmation_token(email: str) -> str | bytes:
    """Generate unique token for verifying new user's email.

    :param email: Email of recipient.
    :return: Unique token for user to authenticate with.
    """
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(
        email, salt=current_app.config["SECURITY_PASSWORD_SALT"]
    )


def confirm_token(token: str, max_age: int = 3600) -> str:
    """Confirm token for verifying new user's email.

    :param token: Token to serialize with secret key.
    :param max_age: Max age of token before considered invalid.
    :return: Return user's email if valid.
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
    :return: A unique token hashed from user's ID.
    """
    return jwt.encode(
        {"reset_password": user_id, "exp": time() + max_age},
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )


def get_requested_reset_password_user(token: str) -> User:
    """Decode the user's token and return the user model.

    :param token: Token to decrypt.
    :return: User, if the token is valid, else None.
    """
    id = jwt.decode(
        token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
    )["reset_password"]
    return User.query.get(id)
