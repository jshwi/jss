"""
app.utils.send_from
===================
"""
import os
from pathlib import Path
from typing import Any, Optional, Union

from flask import Response, current_app, send_from_directory


def static(path: Union[os.PathLike, str], **kwargs: Any) -> Response:
    """Serve file from the static directory.

    :param path: The path to the file, relative to the static directory.
    :param kwargs: Any additional keyword arguments to pass to
        ``flask.send_from_directory``.
    :return: Response object.
    """
    static_folder = current_app.static_folder or ""
    return send_from_directory(static_folder, path, **kwargs)


def image(
    path: str, image_type: Optional[str] = None, **kwargs: Any
) -> Response:
    """Serve image from the static directory.

    :param path: The path to the file relative to the img dir.
    :param image_type: The suffix to the ``image/`` section of the
        declared mimetype. If no ``image_type`` if provided, then the
        images extension will be the assumed mimetype.
    :param kwargs: Any additional keyword arguments to pass to
        ``static``.
    :return: Response object.
    """
    image_type = image_type or path.split(".", maxsplit=1)[-1]
    fullpath = Path("img") / path
    return static(fullpath, mimetype=f"image/{image_type}", **kwargs)
