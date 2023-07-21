"""
app.exceptions
==============

Register handling of error-codes and their corresponding pages.
"""
from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, render_template
from werkzeug.exceptions import HTTPException


def init_app(app: Flask) -> None:
    """Register error handlers.

    :param app: Application factory object.
    """
    exceptions = {
        int(k): v
        for k, v in json.loads(
            (Path(__file__).parent / "schemas" / "exceptions.json").read_text(
                encoding="utf-8"
            )
        ).items()
    }

    def render_error(error: HTTPException) -> tuple[str, int]:
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
                exception=exceptions[error_code],
            ),
            error_code,
        )

    for errcode in exceptions:
        app.errorhandler(errcode)(render_error)
