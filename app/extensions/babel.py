"""
app.extensions.babel
====================
"""
from flask import Flask, request
from flask_babel import Babel as _Babel


class Babel(_Babel):
    """Subclass `flask_babel.Babel`."""

    def init_app(self, app: Flask) -> None:
        super().init_app(app)
        self.localeselector(
            lambda: request.accept_languages.best_match(
                app.config["LANGUAGES"]
            )
        )
