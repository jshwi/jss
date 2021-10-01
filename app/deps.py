"""
app.deps
========
"""
from flask import Flask
from redis import Redis
from rq import Queue


def init_app(app: Flask) -> None:
    """Register application background task handlers.

    :param app: Flask app.
    """
    app.redis = Redis.from_url(app.config["REDIS_URL"])  # type: ignore
    app.task_queue = Queue("jss-tasks", connection=app.redis)  # type: ignore
