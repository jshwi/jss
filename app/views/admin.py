"""
app.views.admin
===============
"""

from flask import Blueprint, render_template

blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@blueprint.route("/")
def admin() -> str:
    """Render admin page.

    :return: Rendered admin page.
    """
    return render_template("admin.html")
