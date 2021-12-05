"""
app
===

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

    * Config object from config module
    * Loggers from logging
    * Dependencies that aren't part of an extension package.
    * Extensions, prefixed with ``Flask-``; includes ``init_app`` method
    * Blueprints containing routing logic
    * Exceptions for handling error pages
    * Shell commands for manipulating state with ``flask shell``
    * Commandline arguments
    * Admin page, which does not work effectively with ``init_app`` (the
      method, not the module function)
    * Navbar for rendering DOM Python-side
"""
from flask import Flask

from app import (
    cli,
    config,
    deps,
    dom,
    exceptions,
    extensions,
    log,
    routes,
    security,
    shell,
)

__version__ = "1.13.3"


def create_app() -> Flask:
    """Create ``Flask`` web application object.

    Accessible through wsgi.py or if ``FLASK_ENV`` is set to package.

    :return: Web application initialized and processed through factory
        pattern.
    """
    app = Flask(__name__)
    config.init_app(app)
    log.init_app(app)
    deps.init_app(app)
    extensions.init_app(app)
    routes.init_app(app)
    exceptions.init_app(app)
    shell.init_app(app)
    cli.init_app(app)
    dom.init_app(app)
    security.init_app(app)
    return app
