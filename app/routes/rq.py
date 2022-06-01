"""
app.rotes.rq
============
"""
import rq_dashboard
from flask import Flask

from app.utils.security import admin_required


@admin_required
def rq_authorization_required() -> None:
    """Allow authorization for ``rq-dashboard``."""


def init_app(app: Flask) -> None:
    """Register ``rq-dashboard`` blueprint."""
    rq_dashboard.blueprint.before_request(rq_authorization_required)
    app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")
