"""
app.cli
=======

Define app's commandline functions.
"""
import click
from flask import Flask
from flask.cli import with_appcontext

from .models import init_db


@click.group()
def create() -> None:
    """App init methods."""


@create.command("db")
@with_appcontext
def create_db_command() -> None:
    """initialize database."""
    init_db()
    click.echo("Initialized database")


def init_app(app: Flask) -> None:
    """Initialize the app cli.

    :param app: App object.
    """
    app.cli.add_command(create)
