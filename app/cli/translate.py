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


def _pybabel(positional: str, *args: str | os.PathLike) -> None:
    subprocess.run(["pybabel", positional, *args], check=True)


def _add_translator() -> None:
    pot_file = Path("messages.pot")
    pot_file.write_text(
        pot_file.read_text(encoding="utf-8")
        .replace("FIRST AUTHOR", current_app.config["COPYRIGHT_AUTHOR"])
        .replace("FULL NAME", current_app.config["COPYRIGHT_AUTHOR"])
        .replace("EMAIL@ADDRESS", current_app.config["COPYRIGHT_EMAIL"]),
        encoding="utf-8",
    )


def _remove_headers(file: Path) -> None:
    """Remove problematic headers (e.g. that cause merge conflicts)."""
    lines = []
    for line in file.read_text(encoding="utf-8").splitlines():
        if not line.startswith('"POT-Creation-Date:'):
            lines.append(line)

    file.write_text("\n".join(lines), encoding="utf-8")


def _pybabel_extract() -> None:
    _pybabel(
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
    )
    _add_translator()


def _pybabel_update() -> None:
    _pybabel(
        "update",
        "--input-file",
        "messages.pot",
        "--output-dir",
        current_app.config["TRANSLATIONS_DIR"],
    )


def _pybabel_compile() -> None:
    _pybabel("compile", "--directory", current_app.config["TRANSLATIONS_DIR"])


def _pybabel_init(lang: str) -> None:
    _pybabel(
        "init",
        "--input-file",
        "messages.pot",
        "--output-dir",
        current_app.config["TRANSLATIONS_DIR"],
        "--locale",
        lang,
    )


def translate_update_cli() -> None:
    """Update all languages."""
    _pybabel_extract()
    _pybabel_update()
    for lang in current_app.config["TRANSLATIONS_DIR"].iterdir():
        file = lang / "LC_MESSAGES" / "messages.po"
        _remove_headers(file)

    os.remove("messages.pot")


def translate_compile_cli() -> None:
    """Compile all languages."""
    tdir: Path = current_app.config["TRANSLATIONS_DIR"]
    if tdir.is_dir():
        for lang in current_app.config["TRANSLATIONS_DIR"].iterdir():
            catalog = lang / "LC_MESSAGES" / "messages.po"
            if catalog.is_file():
                _pybabel_compile()
                break
    else:
        print("No message catalogs to compile")


def translate_init_cli(lang: str) -> None:
    """Initialize a new language.

    :param lang: Language to initialize.
    """
    _pybabel_extract()
    _pybabel_init(lang)
    file = (
        current_app.config["TRANSLATIONS_DIR"]
        / lang
        / "LC_MESSAGES"
        / "messages.po"
    )
    _remove_headers(file)
    os.remove("messages.pot")


@click.group()
def translate() -> None:
    """Translation and localization commands."""
    # group functions are registered as decorators, and this will
    # decorate its subcommands, not `click`


@translate.command("update")
@with_appcontext
def _update() -> None:
    """Update all languages."""
    translate_update_cli()


@translate.command("compile")
@with_appcontext
def _compile() -> None:
    """Compile all languages."""
    translate_compile_cli()


@translate.command("init")
@click.argument("lang")
@with_appcontext
def _init(lang: str) -> None:
    """Initialize a new language.

    :param lang: Language to initialize.
    """
    translate_init_cli(lang)
