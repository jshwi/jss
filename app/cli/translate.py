"""
app.cli.translate
=================

Run translation actions.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import click
from flask import current_app
from flask.cli import with_appcontext

from app.version import __version__


def _remove_headers(file: Path) -> None:
    """Remove problematic headers (e.g. that cause merge conflicts)."""
    lines = []
    for line in file.read_text(encoding="utf-8").splitlines():
        if not line.startswith('"POT-Creation-Date:'):
            lines.append(line)

    file.write_text("\n".join(lines), encoding="utf-8")


def _pybabel_extract() -> None:
    subprocess.run(
        [
            "pybabel",
            "extract",
            "--keywords=_l",
            "--width=79",
            "--msgid-bugs-address",
            current_app.config["COPYRIGHT_EMAIL"],
            "--copyright-holder",
            current_app.config["COPYRIGHT_AUTHOR"],
            "--project",
            Path.cwd().name,
            "--version",
            __version__,
            "--mapping-file",
            "babel.cfg",
            "--output-file",
            "messages.pot",
            ".",
        ],
        check=True,
    )
    pot_file = Path("messages.pot")
    pot_file.write_text(
        pot_file.read_text(encoding="utf-8")
        .replace("FIRST AUTHOR", current_app.config["COPYRIGHT_AUTHOR"])
        .replace("FULL NAME", current_app.config["COPYRIGHT_AUTHOR"])
        .replace("EMAIL@ADDRESS", current_app.config["COPYRIGHT_EMAIL"]),
        encoding="utf-8",
    )


@click.group()
def translate() -> None:
    """Commands related to language translation."""


@translate.command()
@with_appcontext
def update() -> None:
    """Update all languages."""
    _pybabel_extract()
    subprocess.run(
        [
            "pybabel",
            "update",
            "--input-file",
            "messages.pot",
            "--output-dir",
            current_app.config["TRANSLATIONS_DIR"],
        ],
        check=True,
    )
    for lang in current_app.config["TRANSLATIONS_DIR"].iterdir():
        if lang.is_dir():
            _remove_headers(lang / "LC_MESSAGES" / "messages.po")

    os.remove("messages.pot")


# noinspection PyShadowingBuiltins
@translate.command()
@with_appcontext
def compile() -> None:  # pylint: disable=redefined-builtin
    """Compile all languages."""
    for lang in current_app.config["TRANSLATIONS_DIR"].iterdir():
        catalog = lang / "LC_MESSAGES" / "messages.po"
        if catalog.is_file():
            subprocess.run(
                [
                    "pybabel",
                    "compile",
                    "--directory",
                    current_app.config["TRANSLATIONS_DIR"],
                ],
                check=True,
            )
            break


@translate.command()
@click.argument("lang")
@with_appcontext
def init(lang: str) -> None:
    """Initialize a new language.

    :param lang: Language to initialize.
    """
    _pybabel_extract()
    subprocess.run(
        [
            "pybabel",
            "init",
            "--input-file",
            "messages.pot",
            "--output-dir",
            current_app.config["TRANSLATIONS_DIR"],
            "--locale",
            lang,
        ],
        check=True,
    )
    _remove_headers(
        current_app.config["TRANSLATIONS_DIR"]
        / lang
        / "LC_MESSAGES"
        / "messages.po"
    )
    os.remove("messages.pot")


@translate.command()
@with_appcontext
def readme() -> None:
    """List supported languages.."""
    languages = []
    markdown = current_app.config["TRANSLATIONS_DIR"] / "LANGUAGES.md"
    for path in current_app.config["TRANSLATIONS_DIR"].iterdir():
        if path.is_dir():
            languages.append(
                "- {}\n".format(
                    (path / "LC_MESSAGES" / "messages.po")
                    .read_text(encoding="utf-8")
                    .split()[1]
                )
            )

    markdown.write_text(
        f"# Languages\n\n{'\\n'.join(sorted(languages))}",
        encoding="utf-8",
    )
    print("readme written successfully")
