"""
app.user
========
"""
from typing import Any

from .models import User, db


def create_user(
    username: str, email: str, password: str, **kwargs: Any
) -> User:
    """Instantiate a new user, add user to the database, and return.

    :param username:    New user's username.
    :param email:       New user's email address.
    :param password:    New user's password.
    :param kwargs:      Non-mandatory keyword arguments to pas to model.
    :return:            New ``User`` object.
    """
    user = User(username=username, email=email, **kwargs)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
