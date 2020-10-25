"""
app
===

Application factory.
"""
from flask import Flask

from . import cli, config, exceptions, extensions, models, routes

__version__ = "0.1.0"


def create_app() -> Flask:
    """Create ``Flask`` web application object.

    :return:    Web application initialized with config, database,
                extensions, and routes
    """
    app = Flask(__name__)
    config.init_app(app)
    models.init_app(app)
    extensions.init_app(app)
    routes.init_app(app)
    exceptions.init_app(app)
    cli.init_app(app)
    return app
