"""
app.utils.user
==============

Functionality for user's of the app.
"""
import typing as t
from datetime import datetime
from getpass import getpass

from flask import current_app

from app.extensions import login_manager
from app.models import User, Usernames, db


def create_user(
    username: str, email: str, password: str, **kwargs: t.Any
) -> User:
    """Instantiate a new user, add user to the database, and return.

    :param username: New user's username.
    :param email: New user's email address.
    :param password: New user's password.
    :param kwargs: Non-mandatory keyword arguments to pas to model.
    :return: New ``User`` object.
    """
    # noinspection PyArgumentList
    user = User(username=username, email=email, **kwargs)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    user = User.resolve_all_names(username=username)
    # noinspection PyArgumentList
    usernames = Usernames(username=user.username, user_id=user.id)
    db.session.add(usernames)
    db.session.commit()
    return user


def create_user_override(
    username: str, email: str, password: str, **kwargs: t.Any
) -> User:
    """Create a new user and confirm them automatically.

    :param username: New user's username.
    :param email: New user's email address.
    :param password: New user's password.
    :param kwargs: Additional keyword args to pass to user model.
    :return: New ``User`` object.
    """
    return create_user(
        username,
        email,
        password,
        confirmed=True,
        confirmed_on=datetime.now(),
        **kwargs,
    )


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

    create_user_override(username, email, password)
    print("user successfully created")


def create_admin_cli() -> None:
    """Create admin user."""
    if User.query.get(1) is None:
        # no need to add to the app config
        # this will only need to be called once
        # raising an error won't be necessary after the first time
        create_user_override(
            username="admin",
            email=current_app.config["ADMINS"][0],
            password=current_app.config["ADMIN_SECRET"],
            admin=True,
            authorized=True,
        )
        print("admin successfully created")


@login_manager.user_loader
def user_login(id: int) -> User:
    """Wrap the user object.

    :param id: User id to get.
    :return: Returned user object.
    """
    return User.query.get(id)
