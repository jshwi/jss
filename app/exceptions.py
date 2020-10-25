"""
app.errors
==========
"""
from typing import Any

from flask import Flask, render_template


def init_app(app: Flask) -> None:
    """Register error handlers."""

    def render_error(error: Exception) -> Any:
        """Render error template."""
        # if a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        # noinspection PyUnresolvedReferences
        return render_template(f"error/{error_code}.html"), error_code

    for errcode in [400, 401, 404, 405, 500]:
        app.errorhandler(errcode)(render_error)
