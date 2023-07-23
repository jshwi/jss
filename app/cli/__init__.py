"""
app.cli
=======

Define app's commandline functions.
"""
import click
from flask import Flask
from flask.cli import with_appcontext

from app.utils.lang import (
    translate_compile_cli,
    translate_init_cli,
    translate_update_cli,
)
from app.utils.user import create_admin_cli, create_user_cli


@click.group()
def create() -> None:
    """Create users."""
    # group functions are registered as decorators, and this will
    # decorate its subcommands, not `click`


@create.command("user")
@with_appcontext
def create_user() -> None:
    """Create a new user with the commandline instead of web form."""
    create_user_cli()


@create.command("admin")
@with_appcontext
def create_admin() -> None:
    """Create a new admin with the commandline instead of web form."""
    create_admin_cli()


@click.group()
def translate() -> None:
    """Translation and localization commands."""
    # group functions are registered as decorators, and this will
    # decorate its subcommands, not `click`


@translate.command("update")
@with_appcontext
def translate_update() -> None:
    """Update all languages."""
    translate_update_cli()


@translate.command("compile")
@with_appcontext
def translate_compile() -> None:
    """Compile all languages."""
    translate_compile_cli()


@translate.command("init")
@click.argument("lang")
@with_appcontext
def translate_init(lang: str) -> None:
    """Initialize a new language.

    :param lang: Language to initialize.
    """
    translate_init_cli(lang)


def init_app(app: Flask) -> None:
    """Initialize the app commandline.

    :param app: Application factory object.
    """
    app.cli.add_command(create)
    app.cli.add_command(translate)
