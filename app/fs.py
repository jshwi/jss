"""
app.fs
======
"""
from pathlib import Path


def create_gitignore(path: Path) -> None:
    """Create a .gitignore file to exclude dir from versioning.

    :param path: Path to dir to exclude.
    """
    gitignore = path / ".gitignore"
    path.mkdir(exist_ok=True, parents=True)
    gitignore.write_text("*", encoding="utf-8")
