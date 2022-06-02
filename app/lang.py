"""
app.lang
========
"""
from flask import Flask, request

from app.extensions import babel


def init_app(app: Flask) -> None:
    """Initialize language functionality.

    :param app: Application factory object.
    """
    babel.localeselector(
        lambda: request.accept_languages.best_match(app.config["LANGUAGES"])
    )
