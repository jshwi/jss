"""
app.cli
=======

Application's custom commands.

Includes commands defined in this app only. The application will have
additional commands that come preloaded with ``Flask`` such as
``flask run`` and ``flask shell``. It is likely this application will
have even more commands than just these such as those defined in
third-party extensions e.g. ``flask db`` from ``flask_migrate`` and
``flask digest`` from ``flask_static_digest``.

For all available commands run ``flask --help``.
"""

from flask import Flask

from app.cli import create, lexers, translate


def init_app(app: Flask) -> None:
    """Initialize commands belonging to this module.

    :param app: Application object.
    """
    app.cli.add_command(create.create)
    app.cli.add_command(translate.translate)
    app.cli.add_command(lexers.lexers)
