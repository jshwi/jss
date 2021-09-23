"""
app.shell
=========
"""
from flask import Flask

from .models import Message, Notification, Post, User, db


def register_models(app: Flask) -> None:
    """Make database models accessible to the ``Flash`` shell.

    :param app: Flask app.
    """
    app.shell_context_processor(
        lambda: {
            "db": db,
            "User": User,
            "Post": Post,
            "Message": Message,
            "Notification": Notification,
        }
    )


def init_app(app: Flask) -> None:
    """Register shell context objects.

    :param app: Flask app.
    """
    register_models(app)
