"""
app.route.favicon
=================
"""
from flask import Blueprint, Response

from app.utils import send_from

blueprint = Blueprint("static", __name__)


@blueprint.route("/favicon.ico")
def favicon_ico() -> Response:
    """Serve image to the root of the application.

    :return: Response object.
    """
    return send_from.image("favicon.ico", image_type="png")
