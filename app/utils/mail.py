"""
app.utils.mail
==============

Setup app's mailer.
"""
import typing as t
from threading import Thread

from flask import Flask, current_app
from flask_mail import Message

from app.extensions import mail


def _send_async_email(app: Flask, msg: Message) -> None:
    with app.app_context():
        mail.send(msg)


def send_email(
    attachments: t.Optional[t.Iterable[t.Dict[str, str]]] = None,
    sync: bool = False,
    **kwargs: t.Any,
) -> None:
    """Send a threaded email.

    Without threading the app will wait until the email has been sent
    before continuing.

    In order to access the application context for this function a
    protected ``werkzeug`` attribute has to be accessed.
    From https://blog.miguelgrinberg.com/post/
    ``the-flask-mega-tutorial-part-xv-a-better-application-structure``:

        Using current_app directly in the send_async_email() function
        that runs as a background thread would not have worked, because
        current_app is a context-aware variable that is tied to the
        thread that is handling the client request.  In a different
        thread, current_app would not have a value assigned.

        Passing current_app directly as an argument to the thread object
        would not have worked either, because current_app is really a
        proxy object that is dynamically mapped to the application
        instance. So passing the proxy object would be the same as using
        current_app directly in the thread.

        What I needed to do is access the real application instance that
        is stored inside the proxy object, and pass that as the app
        argument. The current_app._get_current_object() expression
        extracts the actual application instance from inside the proxy
        object, so that is what I passed to the thread as an argument.

    Note: Keyword args (dict) to pass to ``attachments``:

        See ``flask_mail.Message.attach``.

        * filename:     filename of attachment
        * content_type: file mimetype
        * data:         the raw file data

    :param attachments: Iterable of kwargs to construct attachment.
    :param sync: Don't thread if True: Defaults to False.
    :param kwargs: Keyword args to pass to ``Message``:
        See ``flask_mail.Message``.
    """
    # noinspection PyProtectedMember
    # pylint: disable=protected-access
    app = current_app._get_current_object()  # type: ignore
    subject_prefix = app.config["MAIL_SUBJECT_PREFIX"]
    subject = kwargs.get("subject", "")
    kwargs["subject"] = f"{subject_prefix}{subject}"
    kwargs["sender"] = kwargs.get("sender", app.config["DEFAULT_MAIL_SENDER"])
    message = Message(**kwargs)
    if attachments:
        for attachment in attachments:
            message.attach(**attachment)

    if sync:
        mail.send(message)
    else:
        thread = Thread(target=_send_async_email, args=(app, message))
        thread.start()
