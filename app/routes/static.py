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
    return send_from.image("favicon.ico", image_type="vnd.microsoft.icon")


@blueprint.route("/android-chrome-192x192.png")
def android_chrome_192x192_png() -> Response:
    """Serve image to the root of the application.

    :return: Response object.
    """
    return send_from.image("android-chrome-192x192.png")


@blueprint.route("/android-chrome-512x512.png")
def android_chrome_512x512_png() -> Response:
    """Serve image to the root of the application.

    :return: Response object.
    """
    return send_from.image("android-chrome-512x512.png")


@blueprint.route("/apple-touch-icon.png")
def apple_touch_icon_png() -> Response:
    """Serve image to the root of the application.

    :return: Response object.
    """
    return send_from.image("apple-touch-icon.png")


@blueprint.route("/favicon-16x16.png")
def favicon_16x16_png() -> Response:
    """Serve image to the root of the application.

    :return: Response object.
    """
    return send_from.image("favicon-16x16.png")


@blueprint.route("/favicon-32x32.png")
def favicon_32x32_png() -> Response:
    """Serve image to the root of the application.

    :return: Response object.
    """
    return send_from.image("favicon-32x32.png")


@blueprint.route("/mstile-150x150.png")
def mstile_150x150_png() -> Response:
    """Serve image to the root of the application.

    :return: Response object.
    """
    return send_from.image("mstile-150x150.png")


@blueprint.route("/safari-pinned-tab.svg")
def safari_pinned_tab_svg() -> Response:
    """Serve image to the root of the application.

    :return: Response object.
    """
    return send_from.image("safari-pinned-tab.svg", image_type="svg+xml")


@blueprint.route("/site.webmanifest")
def site_webmanifest() -> Response:
    """Serve webmanifest to the root of the application.

    :return: Response object.
    """
    return send_from.static(
        "site.webmanifest", mimetype="application/manifest+json"
    )


@blueprint.route("/browserconfig.xml")
def browser_config_xml() -> Response:
    """Serve browser config to the root of the application.

    :return: Response object.
    """
    return send_from.static("browserconfig.xml", mimetype="application/xml")
