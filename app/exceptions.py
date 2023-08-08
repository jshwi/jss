"""
app.exceptions
==============

Register handling of error-codes and their corresponding pages.
"""
from __future__ import annotations

import json

from flask import Flask, render_template
from werkzeug.exceptions import HTTPException


def init_app(app: Flask) -> None:
    """Initialize error pages for this application.

    See `exceptions`_.

    .. _exceptions:
        https://github.com/jshwi/jss/blob/master/app/schemas/
        exceptions.json

    :param app: Application object.
    """
    exceptions = {
        int(k): v
        for k, v in json.loads(
            (app.config["SCHEMAS"] / "exceptions.json").read_text(
                encoding="utf-8"
            )
        ).items()
    }

    def render_error(error: HTTPException) -> tuple[str, int]:
        # not considered error for logging as all "errors" will be
        # emailed
        app.logger.info(error.description)
        error_code = getattr(error, "code", 500)
        return (
            render_template(
                "exception.html",
                error_code=error_code,
                exception=exceptions[error_code],
            ),
            error_code,
        )

    # render error template.
    # If a HTTPException pull the ``code`` attribute; default to 500
    for errcode in exceptions:
        app.errorhandler(errcode)(render_error)
