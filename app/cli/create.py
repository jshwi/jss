"""
app.cli.create
==============

Add assets to database.
"""
from datetime import datetime
from getpass import getpass

import click
from flask import current_app
from flask.cli import with_appcontext

from app.models import User
from app.user import create_user


def create_user_override(
    username: str, email: str, password: str, **kwargs: object
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


@click.group()
def create() -> None:
    """Create users."""
    # group functions are registered as decorators, and this will
    # decorate its subcommands, not `click`


@create.command("user")
@with_appcontext
def user() -> None:
    """Create a new user with the commandline instead of web form."""
    create_user_cli()


@create.command("admin")
@with_appcontext
def admin() -> None:
    """Create a new admin with the commandline instead of web form."""
    create_admin_cli()
