"""
app.deps
========

Register dependencies that are not part of a ``Flask`` extension.
"""
from flask import Flask
from redis import Redis
from rq import Queue


def init_app(app: Flask) -> None:
    """Register application helpers that are not ``Flask-`` extensions.

    As these are not ``Flask`` extensions they do not have an
    ``init_app`` method, and so can be attached to the app by declaring
    them as instance attributes.

    .. todo:: These are not declared in ``__init__`` and are a bit of a
        code-smell. Using ``flask.g`` may be more appropriate...

    :param app: Application factory object.
    """
    app.redis = Redis.from_url(app.config["REDIS_URL"])  # type: ignore
    app.task_queue = Queue("jss-tasks", connection=app.redis)  # type: ignore
