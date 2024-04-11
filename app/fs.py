"""
app.fs
======
"""

from pathlib import Path

from flask import Flask


def create_gitignore(path: Path) -> None:
    """Create a .gitignore file to exclude dir from versioning.

    :param path: Path to dir to exclude.
    """
    gitignore = path / ".gitignore"
    path.mkdir(exist_ok=True, parents=True)
    gitignore.write_text("*", encoding="utf-8")


def init_app(app: Flask) -> None:
    """Initialize filesystem.

    :param app: Application object.
    """
    create_gitignore(app.config["STATIC_FOLDER"] / "uploads")
