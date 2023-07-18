"""
app.cli.translate
=================

Run translation actions.
"""
import click
from flask.cli import with_appcontext

from app.utils.lang import (
    translate_compile_cli,
    translate_init_cli,
    translate_update_cli,
)


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
