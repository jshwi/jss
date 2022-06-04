"""
app.dom
=======
"""
from flask import Flask

from app.dom import macros, text
from app.utils.register import RegisterContext


def init_app(app: Flask) -> None:
    """Initialize navbar.

    :param app: Application factory object.
    """
    app.context_processor(RegisterContext.registered)
