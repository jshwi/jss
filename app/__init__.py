"""A Flask webapp.

Application factory.

From the ``Flask`` docs:

    Instead of creating a ``Flask`` instance globally, we will create
    it inside a function. This function is known as the application
    factory. Any configuration, registration, and other set up the
    application needs will happen inside the function, then the
    application will be returned.

The app will be passed through to each ``init_app`` declaration, unique
to its respective module. These functions will configure the app
designed in this package.

Registers:

    * This app's commandline interface
    * Config object from config module
    * Exceptions for handling error pages
    * This app's registered ``Flask`` extensions
    * Loggers from logging
    * Blueprints containing routing logic
    * This app's interactive shell
"""
from flask import Flask

from app import cli, config, exceptions, extensions, fs, log, shell, views
from app.version import __version__


def create_app() -> Flask:
    """Create ``Flask`` web application object.

    Accessible through wsgi.py.

    :return: Web application initialized and processed through factory
        pattern.
    """
    app = Flask(__name__)
    config.init_app(app)
    log.init_app(app)
    extensions.init_app(app)
    views.init_app(app)
    exceptions.init_app(app)
    shell.init_app(app)
    cli.init_app(app)
    fs.init_app(app)
    return app


__all__ = ["__version__", "create_app"]
