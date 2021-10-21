"""
app.errors
==========

Register handling of error-codes and their corresponding pages.
"""
from typing import Tuple

from flask import Flask, render_template

EXCEPTIONS = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}


def init_app(app: Flask) -> None:
    """Register error handlers."""

    def render_error(error: Exception) -> Tuple[str, int]:
        """Render error template.

        If a HTTPException, pull the ``code`` attribute; default to 500.

        :param error: Exception to catch and render page for.
        :return: Tuple consisting of rendered template and error code.
        """
        error_code = getattr(error, "code", 500)
        return (
            render_template(
                "exception.html",
                error_code=error_code,
                exception=EXCEPTIONS[error_code],
            ),
            error_code,
        )

    for errcode in [400, 401, 403, 404, 405, 500]:
        app.errorhandler(errcode)(render_error)
