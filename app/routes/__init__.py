"""
app.routes
==========

A view function is written to respond to application requests.

``Flask`` uses patterns to match the incoming request URL to the view
that should handle it. The view returns data that ``Flask`` turns into
an outgoing response.

``Flask`` can also go the other direction and generate a URL to view
based on its name and arguments.
"""
from flask import Flask

from app.routes import admin, auth, post, public, redirect, user


def init_app(app: Flask) -> None:
    """Load the app with views views.

    :param app: Application factory object.
    """
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.strip_trailing_newlines = False
    app.register_blueprint(public.blueprint)
    app.register_blueprint(auth.blueprint)
    app.register_blueprint(user.blueprint)
    app.register_blueprint(post.blueprint)
    app.register_blueprint(redirect.blueprint)
    app.add_url_rule("/", endpoint="index")
    admin.init_app(app)
