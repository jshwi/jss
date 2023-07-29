"""
app.views
==========

A view function is written to respond to application requests.

``Flask`` uses patterns to match the incoming request URL to the view
that should handle it. The view returns data that ``Flask`` turns into
an outgoing response.

``Flask`` can also go the other direction and generate a URL to view
based on its name and arguments.
"""
from datetime import datetime

from bs4 import BeautifulSoup
from flask import Flask, Response, g
from flask_babel import get_locale
from flask_login import current_user

from app.extensions import db
from app.views import (
    auth,
    database,
    order,
    post,
    public,
    redirect,
    report,
    user,
)


def _before_request() -> None:
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

    g.locale = str(get_locale())


def format_html(response: Response) -> Response:
    """Prettify HTML response.

    See https://stackoverflow.com/a/6167432/13316671.

    :param response: Response returned from a route.
    :return: Response returned from a route.
    """
    if response.content_type == "text/html; charset=utf-8":
        response.set_data(
            BeautifulSoup(  # type: ignore
                response.get_data(as_text=True), "html.parser"
            ).prettify(formatter="html")
        )

    return response


def init_app(app: Flask) -> None:
    """Load the app with views.

    :param app: Application factory object.
    """
    app.before_request(_before_request)
    app.register_blueprint(report.blueprint)
    app.register_blueprint(public.blueprint)
    app.register_blueprint(auth.blueprint)
    app.register_blueprint(user.blueprint)
    app.register_blueprint(post.blueprint)
    app.register_blueprint(redirect.blueprint)
    app.register_blueprint(order.blueprint)
    app.add_url_rule("/", endpoint="index")
    database.init_app(app)
    app.after_request(format_html)  # type: ignore
