"""
app.views.upload
================
"""

from __future__ import annotations

import imghdr
import os
import typing as t
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import login_required
from werkzeug import Response
from werkzeug.utils import secure_filename

from app.extensions import csrf_protect
from app.views.forms import UploadForm
from app.views.security import admin_required

blueprint = Blueprint("upload", __name__, url_prefix="/upload")


def validate_image(stream: t.IO[bytes]) -> str | None:
    """Confirm an image is what it claims to be.

    :param stream: Bytes stream.
    :return: String if file valid, else None for invalid file.
    """
    header = stream.read(512)
    stream.seek(0)
    _format = imghdr.what(None, header)
    if not _format:
        return None

    return f".{_format if _format != 'jpeg' else 'jpg'}"


@csrf_protect.exempt
@blueprint.route("/favicon", methods=["GET", "POST"])
@login_required
@admin_required
def favicon() -> str | Response:
    """Upload a favicon.

    :return: Template or response object.
    """
    form = UploadForm()
    if form.validate_on_submit():
        file = Path(secure_filename(form.file.data.filename))
        if file.suffix not in current_app.config[
            "UPLOAD_EXTENSIONS"
        ] or file.suffix != validate_image(form.file.data.stream):
            flash(
                f"{file} is not a valid {file.suffix} file,"
                " cannot confirm validity of file"
            )
            abort(400)

        path = current_app.config["UPLOAD_PATH"] / file
        form.file.data.save(path)
        os.rename(path, path.parent / "favicon.ico")
        flash(f"{form.file.data.filename} uploaded successfully")
        return redirect(url_for("upload.favicon"))

    return render_template("upload.html", form=form)
