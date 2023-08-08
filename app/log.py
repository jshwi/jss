"""
app.log
=======

Register custom app loggers.
"""
import logging
from logging.handlers import SMTPHandler

from flask import Flask

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(module)s %(message)s"
)


def smtp_handler(app: Flask) -> None:
    """Configure an SMTP handler for error reporting.

    :param app: Application object.
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


def integrate_loggers(app: Flask) -> None:
    """Integrate ``Flask`` logger with ``Gunicorn`` logger.

    https://trstringer.com/logging-flask-gunicorn-the-manageable-way/

    :param app: Application object.
    """
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


def init_app(app: Flask) -> None:
    """Initialize application loggers.

    :param app: Application object.
    """
    smtp_handler(app)
    if not app.config["DEBUG"]:
        integrate_loggers(app)
