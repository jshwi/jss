"""
app.extensions
==============

Each extension is initialized in the app factory located in app.py.
"""
from flask import Flask
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_static_digest import FlaskStaticDigest

debug_toolbar = DebugToolbarExtension()
static_digest = FlaskStaticDigest()
cache = Cache()
db = SQLAlchemy()
migrate = Migrate()


def init_app(app: Flask) -> None:
    """Register ``Flask`` extensions.

    :param app: App object.
    """
    debug_toolbar.init_app(app)
    static_digest.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
