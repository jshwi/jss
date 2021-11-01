"""
app.html
========
"""
from flask import Flask
from flask_nav import register_renderer

from app.dom.navbar import top
from app.dom.renderers import NavbarRenderer
from app.extensions import nav
from app.utils.register import RegisterContext


def init_app(app: Flask) -> None:
    """Initialize navbar.

    :param app: Application factory object.
    """
    register_renderer(app, "navbar_renderer", NavbarRenderer)
    nav.register_element("top", top)
    app.context_processor(RegisterContext.registered)
