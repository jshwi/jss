"""
app.cli
=======

Define app's commandline functions.
"""

import click
from flask import Flask
from flask.cli import with_appcontext

from .user import create_user_cli


@click.group()
def create() -> None:
    """App init methods."""


@create.command("user")
@with_appcontext
def create_user() -> None:
    """Create a new user with cli instead of forms."""
    create_user_cli()


def init_app(app: Flask) -> None:
    """Initialize the app cli.

    :param app: App object.
    """
    app.cli.add_command(create)
