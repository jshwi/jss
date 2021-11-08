"""
app.logging
===========

Register custom app loggers.
"""
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from pathlib import Path

import appdirs
from flask import Flask

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(module)s %(message)s"
)


def smtp_handler(app: Flask) -> None:
    """Configure an SMTP handler for error reporting.

    :param app: Application factory object.
    :return: SMTPHandler if not in debug and vars are set, else None.
    """
    server = app.config["MAIL_SERVER"]
    username = app.config["MAIL_USERNAME"]
    password = app.config["MAIL_PASSWORD"]
    admins = app.config["ADMINS"]
    valid_data = all(i is not None for i in (server, username, password))
    secure = None
    if not app.debug and valid_data and admins:
        auth = (username, password)
        if app.config["MAIL_USE_TLS"]:
            secure = ()

        handler = SMTPHandler(
            mailhost=(server, app.config["MAIL_PORT"]),
            fromaddr=f"no-reply@{server}",
            toaddrs=admins,
            subject="Application Failure",
            credentials=auth,
            secure=secure,
        )
        handler.setLevel(logging.ERROR)
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)


def file_handler(app: Flask) -> None:
    """Add handler to write logs to rotating file.

    :param app: Application factory object.
    :return: Rotating file handler.
    """
    logfile = (
        Path(appdirs.user_log_dir(app.name, opinion=False)) / f"{app.name}.log"
    )
    logfile.parent.mkdir(exist_ok=True, parents=True)
    handler = RotatingFileHandler(logfile, maxBytes=10240, backupCount=10)
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)


def integrate_loggers(app: Flask) -> None:
    """Integrate ``Flask`` logger with ``Gunicorn`` logger.

    https://trstringer.com/logging-flask-gunicorn-the-manageable-way/

    :param app: Application factory object.
    """
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


def init_app(app: Flask) -> None:
    """Add handlers to app logger.

    :param app: Application factory object.
    """
    smtp_handler(app)
    file_handler(app)
    if not app.config["DEBUG"]:
        integrate_loggers(app)
