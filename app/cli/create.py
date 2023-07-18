"""
app.cli.create
==============

Add assets to database.
"""
import click
from flask.cli import with_appcontext

from app.utils.user import create_admin_cli, create_user_cli


@click.group()
def create() -> None:
    """Create users."""
    # group functions are registered as decorators, and this will
    # decorate its subcommands, not `click`


@create.command("user")
@with_appcontext
def _user() -> None:
    """Create a new user with the commandline instead of web form."""
    create_user_cli()


@create.command("admin")
@with_appcontext
def _admin() -> None:
    """Create a new admin with the commandline instead of web form."""
    create_admin_cli()
