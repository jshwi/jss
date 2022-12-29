"""
app.utils.lang
==============
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from flask import current_app

from app.constants import COPYRIGHT_AUTHOR, ENCODING, TRANSLATIONS_DIR
from app.version import __version__

MAPPING = """
[python: app/**.py]
[jinja2: app/templates/**.html]
extensions=jinja2.ext.autoescape,jinja2.ext.with_
"""


#: Evaluated within application context
def _lc_dir() -> Path:
    return Path(f"LC_{current_app.config['BABEL_FILENAME'].upper()}")


#: Evaluated within application context
def _pot_file() -> Path:
    return Path(f"{current_app.config['BABEL_FILENAME']}.pot")


#: Evaluated within application context
def _po_file() -> Path:
    return Path(f"{current_app.config['BABEL_FILENAME']}.po")


def _pybabel(positional: str, *args: str | os.PathLike) -> None:
    subprocess.run(["pybabel", positional, *args], check=True)


def _strip_extra_newline(path: Path) -> None:
    path.write_text(path.read_text()[:-1])


def _add_translator() -> None:
    pot_file = _pot_file()
    pot_file.write_text(
        pot_file.read_text(encoding=ENCODING)
        .replace("FIRST AUTHOR", current_app.config[COPYRIGHT_AUTHOR])
        .replace("FULL NAME", current_app.config[COPYRIGHT_AUTHOR])
        .replace("EMAIL@ADDRESS", current_app.config["COPYRIGHT_EMAIL"]),
        encoding=ENCODING,
    )


def _pybabel_extract() -> None:
    with tempfile.NamedTemporaryFile() as tmp:
        mapping_file = Path(tmp.name)
        mapping_file.write_text(MAPPING, encoding=ENCODING)
        _pybabel(
            "extract",
            "--keywords=_l",
            "--width=79",
            "--msgid-bugs-address",
            current_app.config["COPYRIGHT_EMAIL"],
            "--copyright-holder",
            current_app.config[COPYRIGHT_AUTHOR],
            "--project",
            Path.cwd().name,
            "--version",
            __version__,
            "--mapping-file",
            mapping_file,
            "--output-file",
            _pot_file(),
            ".",
        )
        _add_translator()


def _pybabel_update() -> None:
    _pybabel(
        "update",
        "--input-file",
        _pot_file(),
        "--output-dir",
        current_app.config[TRANSLATIONS_DIR],
    )


def _pybabel_compile() -> None:
    _pybabel("compile", "--directory", current_app.config[TRANSLATIONS_DIR])


def _pybabel_init(lang: str) -> None:
    _pybabel(
        "init",
        "--input-file",
        _pot_file(),
        "--output-dir",
        current_app.config[TRANSLATIONS_DIR],
        "--locale",
        lang,
    )


def translate_update_cli() -> None:
    """Update all languages."""
    _pybabel_extract()
    _pybabel_update()
    for lang in current_app.config[TRANSLATIONS_DIR].iterdir():
        _strip_extra_newline(lang / _lc_dir() / _po_file())

    os.remove(_pot_file())


def translate_compile_cli() -> None:
    """Compile all languages."""
    tdir: Path = current_app.config[TRANSLATIONS_DIR]
    if tdir.is_dir():
        for lang in current_app.config[TRANSLATIONS_DIR].iterdir():
            catalog = lang / _lc_dir() / _po_file()
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
    _strip_extra_newline(
        current_app.config[TRANSLATIONS_DIR] / lang / _lc_dir() / _po_file()
    )
    os.remove(_pot_file())
