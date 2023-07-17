from __future__ import annotations

from flask import Blueprint, render_template, Response

blueprint = Blueprint("cal", __name__, url_prefix="/cal")


@blueprint.route("/")
def register() -> str | Response:
    return render_template("cal.html")
