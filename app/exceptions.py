"""
app.exceptions
==============

Register handling of error-codes and their corresponding pages.
"""
import typing as t

from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

EXCEPTIONS = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}


def init_app(app: Flask) -> None:
    """Register error handlers.

    :param app: Application factory object.
    """

    def render_error(error: HTTPException) -> t.Tuple[str, int]:
        """Render error template.

        If a HTTPException, pull the ``code`` attribute; default to 500.

        :param error: Exception to catch and render page for.
        :return: Tuple consisting of rendered template and error code.
        """
        # not considered error for logging as all "errors" will be
        # emailed
        app.logger.info(error.description)
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
