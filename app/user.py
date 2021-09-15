"""
app.user
========
"""
from getpass import getpass
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


def create_user_cli() -> None:
    """Create a new user."""
    username = input("username: ")
    if User.query.filter_by(username=username).first() is not None:
        print("username is taken")
        return

    email = input("email: ")
    if User.query.filter_by(email=email).first() is not None:
        print("a user with this email address is already registered")
        return

    password = getpass("password: ")
    if getpass("confirm password: ") != password:
        print("passwords do not match: could not add user")
        return

    create_user(username, email, password)
    print("user successfully created")
