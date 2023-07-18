"""
app.cli
=======

Define app's commandline functions.
"""
from flask import Flask

from app.cli import create, translate


def init_app(app: Flask) -> None:
    """Initialize the app commandline.

    :param app: Application factory object.
    """
    app.cli.add_command(create.create)
    app.cli.add_command(translate.translate)
