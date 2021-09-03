"""
app.cli
=======

Define app's commandline functions.
"""
import click
from flask import Flask
from flask.cli import with_appcontext


def command() -> None:
    """Placeholder for future create funcs."""


@click.group()
def create() -> None:
    """App init methods."""


@create.command("command")
@with_appcontext
def create_command() -> None:
    """Placeholder for future create commands."""
    command()


def init_app(app: Flask) -> None:
    """Initialize the app cli.

    :param app: App object.
    """
    app.cli.add_command(create)
