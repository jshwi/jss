"""
app.models
==========

Define app's database models.
"""
import sqlite3
from typing import Optional

from flask import Flask, Response, current_app, g

# rules for initializing a new application database
# the database is designed to store user information and user's post
# information
# the user field mist be unique and the user and password fields cannot
# blank
# each user and post will contain a corresponding id
# the post is bound to the user by referencing the `author_id`
# posts must contain and author id, timestamp, title, and body
# the author's id will be cross referenced as a foreign key
_SCHEMA = """\
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
);\
"""


def get_db() -> sqlite3.Connection:
    """Return a connection to the ``SQLite`` database.

    The connection is stored and reused instead of creating a new
    connection after each invocation.

    This will be called when the application has been created. This is
    the first thing that needs to be done when working with databases.
    Any queries and operations are performed using the connection which
    is closed after the work has finished.

    The connection is instructed to return rows that behave like Python
    dict objects. This allows access to the columns by name.

    The location of the database is defined  with the ``DATABASE_URL``
    configuration key. This file does not need to exist yet and won't
    until the database has been initialized through the commandline.

    :return: Initialized or retrieved SQLite connection object.
    """
    if "db" not in g:
        g.db = sqlite3.connect(  # pylint: disable=assigning-non-slot
            current_app.config["DATABASE_URL"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def _close_db(_: Optional[BaseException] = None) -> Response:
    # close database connection if it is active
    # error passed to function through `teardown_appcontext`
    # no exception handling needs to be made in this function.
    db = g.pop("db", None)
    if db is not None:
        db.close()

    return Response()


def init_db() -> None:
    """Read schema template to initialize database."""
    get_db().executescript(_SCHEMA)


def init_app(app: Flask) -> None:
    """Initialize the app.

    Add callback function to specify the rules of tearing down the app
    after use.

    Add commandline arguments to ``Flask`` .

    :param app: App object.
    """
    app.teardown_appcontext(_close_db)
