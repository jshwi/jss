"""
app.extensions.babel
====================
"""
from flask import Flask, request
from flask_babel import Babel as _Babel


class Babel(_Babel):
    """Subclass ``flask_babel.Babel``.

    With this the ``Babel.init_app`` can be tweaked so that everything
    remains encapsulated in the application factory, with no need to
    add additional functions to the application..
    """

    def init_app(self, app: Flask) -> None:
        super().init_app(app)
        self.localeselector(
            lambda: request.accept_languages.best_match(
                app.config["LANGUAGES"]
            )
        )
