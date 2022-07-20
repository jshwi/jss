"""
tests._test
===========
"""
# pylint: disable=too-many-arguments,too-many-lines,too-many-locals
# pylint: disable=import-outside-toplevel,protected-access
from __future__ import annotations

import fnmatch
import functools
import json
import logging
import os
import shutil
import typing as t
from pathlib import Path

import jinja2.ext as jinja2_ext
import pytest
from flask import Flask, session
from flask.testing import FlaskClient, FlaskCliRunner
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer
from redis import RedisError

from app import config
from app.extensions import mail
from app.log import smtp_handler
from app.models import Post, Task, User
from app.utils import lang
from app.utils.csp import ContentSecurityPolicy, CSPType
from app.utils.mail import send_email
from app.utils.register import RegisterContext

from .const import (
    APP_MODELS_JOB_FETCH,
    APP_UTILS_LANG_POT_FILE,
    APP_UTILS_LANG_SUBPROCESS_RUN,
    COPYRIGHT_AUTHOR,
    COPYRIGHT_EMAIL,
    COPYRIGHT_YEAR,
    COVERED_ROUTES,
    INVALID_OR_EXPIRED,
    LICENSE,
    MAIL_PASSWORD,
    MAIL_PORT,
    MAIL_SERVER,
    MAIL_USERNAME,
    MESSAGES_PO,
    MESSAGES_POT,
    MISC_PROGRESS_INT,
    POT_CONTENTS,
    PYPROJECT_TOML,
    STATUS_CODE_TO_ROUTE_DEFAULT,
    TASK_ID,
    user_email,
    user_password,
    user_username,
)
from .routes import Routes
from .utils import (
    AddTestObjects,
    AuthorizeUserFixtureType,
    GetObjects,
    InterpolateRoutesType,
    PatchGetpassType,
    Recorder,
)


@pytest.mark.usefixtures("init_db")
def test_register(test_app: Flask, routes: Routes) -> None:
    """The register view should render successfully on ``GET``.

    On ``POST``, with valid form data, it should redirect to the login
    URL and the user's data should be in the database. Invalid data
    should display error messages.

    To test that the page renders successfully a simple request is made
    and checked for a ``200 OK`` ``status_code``.

    Headers will have a ``Location`` object with the login URL when the
    register view redirects to the login view.

    :param test_app: Test application.
    :param routes: Work with application routes.
    """
    assert routes.auth.get("/register").status_code == 200
    response = routes.auth.register_index(1)
    assert response.headers["Location"] == "https://localhost/auth/unconfirmed"
    with test_app.app_context():
        assert User.query.get(1) is not None


@pytest.mark.usefixtures("init_db")
def test_login(
    client: FlaskClient, routes: Routes, get_objects: GetObjects
) -> None:
    """Test login functionality.

    :param client: Test application client.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    """
    u_o = get_objects.user(1)
    routes.auth.register_index(1)
    response = routes.auth.login_index(1)
    assert response.headers["Location"] == "https://localhost/auth/unconfirmed"
    with client:
        client.get("/")
        assert current_user.username == u_o[1].username


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize(
    "username,password",
    [
        (user_username[2], user_password[1]),
        (user_username[1], user_password[2]),
    ],
    ids=["incorrect-username", "incorrect-password"],
)
def test_login_validate(
    routes: Routes, get_objects: GetObjects, username: str, password: str
) -> None:
    """Test incorrect username and password error messages.

    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    :param username: Parametrized incorrect username
    :param password: Parametrized incorrect password
    """
    u_o = get_objects.user(1)
    routes.auth.register_index(1)
    u_o[1].username = username
    u_o[1].password = password
    response = routes.auth.login(u_o[1])
    assert b"Invalid username or password" in response.data


@pytest.mark.usefixtures("init_db")
def test_logout(client: FlaskClient, routes: Routes) -> None:
    """Test logout functionality.

    :param client: Client for testing app.
    :param routes: Work with application routes.
    """
    routes.auth.login_index(1)
    with client:
        routes.auth.logout()
        assert "user_id" not in session


# noinspection DuplicatedCode
@pytest.mark.usefixtures("init_db")
def test_index_no_user(client: FlaskClient) -> None:
    """Test login and subsequent requests from the client.

    The index view should display information about the post that was
    added with the test data. When logged in as the author there should
    be a link to edit the post.

    We can also test some more authentication behaviour while testing
    the index view. When not logged in each page shows links to log in
    or register. When logged in there's a link to log out.

    :param client: Client for testing app.
    """
    response = client.get("/")
    assert b"Login" in response.data
    assert b"Register" in response.data


# noinspection DuplicatedCode
@pytest.mark.usefixtures("init_db")
def test_index_user(
    client: FlaskClient,
    routes: Routes,
    get_objects: GetObjects,
    authorize_user: AuthorizeUserFixtureType,
) -> None:
    """Test login and subsequent requests from the client.

    The index view should display information about the post that was
    added with the test data. When logged in as the author there should
    be a link to edit the post.

    We can also test some more authentication behaviour while testing
    the index view. When not logged in each page shows links to log in
    or register. When logged in there's a link to log out.

    :param client: Test application client.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    :param authorize_user: Authorize existing user.
    """
    u_o = get_objects.user(1)
    p_o = get_objects.post(1)
    routes.auth.register_index(1)
    authorize_user(1)
    routes.auth.login_index(1)
    routes.posts.create(1)
    response = client.get("/")
    assert b"Logout" in response.data
    assert p_o[1].title.encode() in response.data
    assert u_o[1].username.encode() in response.data
    assert p_o[1].body.encode() in response.data
    assert b'href="/post/1/update"' in response.data


@pytest.mark.parametrize(
    "route", ["/post/create", "/post/1/update", "/post/1/delete"]
)
def test_login_required(client: FlaskClient, route: str) -> None:
    """Test requirement that user be logged in to post.

    A user must be logged in to access the "create", "update", and
    "delete" views.

    The logged-in user must be the author of the post to access the
    update and delete views, otherwise a ``403 Forbidden`` status is
    returned.

    :param client: Test application client.
    :param route: Parametrized route path.
    """
    assert client.post(route).status_code == 401


@pytest.mark.usefixtures("init_db")
def test_author_required(
    client: FlaskClient,
    routes: Routes,
    authorize_user: AuthorizeUserFixtureType,
) -> None:
    """Test author's name when required.

    The create and update views should render and return a ``200 OK``
    status for a ``GET`` request.

    When valid data is sent in a ``POST`` request the create view should
    insert the new post data into the database and the update view
    should modify the existing data. Both pages should show an error
    message on invalid data.

    :param client: Test application client.
    :param routes: Work with application routes.
    :param authorize_user: Authorize existing user.
    """
    routes.auth.register_index(1)
    routes.auth.register_index(2)
    authorize_user(1)
    authorize_user(2)
    routes.auth.login_index(1)
    routes.posts.create(1)
    routes.auth.logout()
    routes.auth.login_index(2)
    assert routes.posts.update(1, 1).status_code == 403
    assert routes.posts.delete(1).status_code == 403
    response = client.get("/")
    assert b'href="/post/1/update"' not in response.data
    response = client.get("/post/1")
    assert b'href="/post/1/update?revision=-1"' not in response.data


# noinspection DuplicatedCode
@pytest.mark.usefixtures("init_db")
def test_create(
    test_app: Flask, routes: Routes, authorize_user: AuthorizeUserFixtureType
) -> None:
    """Test create view functionality.

    When valid data is sent in a ``POST`` request the create view should
    insert the new post data into the database.

    :param test_app: Test application.
    :param routes: Work with application routes.
    :param authorize_user: Authorize existing user.
    """
    routes.auth.register_index(1)
    authorize_user(1)
    routes.auth.login_index(1)
    assert routes.posts.get("/create").status_code == 200
    routes.posts.create(1)
    with test_app.app_context():
        assert Post.query.count() == 1


@pytest.mark.usefixtures("init_db")
def test_update(
    routes: Routes, authorize_user: AuthorizeUserFixtureType
) -> None:
    """Test update view modifies the existing data.

    :param routes: Work with application routes.
    :param authorize_user: Authorize existing user.
    """
    routes.auth.register_index(1)
    authorize_user(1)
    routes.auth.login_index(1)
    routes.posts.create(1)
    assert b"Edited" not in routes.posts.read(1).data
    routes.posts.update(2, 1)
    assert routes.posts.get("/1/update").status_code == 200
    assert b"Edited" in routes.posts.read(1).data


@pytest.mark.usefixtures("init_db")
def test_delete(
    test_app: Flask, routes: Routes, authorize_user: AuthorizeUserFixtureType
) -> None:
    """Test deletion of posts.

    The "delete" view should redirect to the index URl and the post
    should no longer exist in the database.

    :param test_app: Test ``Flask`` app object.
    :param routes: Work with application routes.
    :param authorize_user: Authorize existing user.
    """
    routes.auth.register_index(1)
    authorize_user(1)
    routes.auth.login_index(1)
    routes.posts.create(1)
    response = routes.posts.delete(1)
    assert response.headers["Location"] == "https://localhost/"
    with test_app.app_context():
        assert Post.query.get(1) is None


@pytest.mark.usefixtures("init_db")
def test_export(
    test_app: Flask,
    routes: Routes,
    get_objects: GetObjects,
    authorize_user: AuthorizeUserFixtureType,
) -> None:
    """Test export to dict_ function for models.

    :param test_app: Test application.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    :param authorize_user: Authorize existing user.
    """
    p_o = get_objects.post(1)
    routes.auth.register_index(1)
    authorize_user(1)
    routes.auth.login_index(1)
    routes.posts.create(1)
    with test_app.app_context():
        as_dict = Post.query.get(1).export()
        assert as_dict["title"] == p_o[1].title
        assert as_dict["body"] == p_o[1].body


@pytest.mark.parametrize("sync", [True, False])
def test_send_mail(
    test_app: Flask, get_objects: GetObjects, sync: bool
) -> None:
    """Test sending of mail by app's email client.

    :param test_app: Test application.
    :param get_objects: Get test objects with db model attributes.
    :param sync: Asynchronous: True or False.
    """
    u_o = get_objects.user(1)
    subject = "mail subject line"
    recipients = [u_o[0].email, u_o[1].email]
    html = "<p>email body<p>"
    sender = "admin@localhost"
    attachment = dict(
        filename="file.txt", content_type="application/json", data="testing"
    )
    with test_app.app_context():
        with mail.record_messages() as outbox:
            send_email(
                subject=subject,
                recipients=recipients,
                html=html,
                sender=sender,
                attachments=[attachment],
                sync=sync,
            )

    assert outbox[0].subject == f"[JSS]: {subject}"
    assert outbox[0].recipients == recipients
    assert outbox[0].html == html
    assert outbox[0].sender == sender
    assert outbox[0].attachments[0].content_type == attachment["content_type"]
    assert outbox[0].attachments[0].data == attachment["data"]
    assert outbox[0].attachments[0].filename == attachment["filename"]


@pytest.mark.usefixtures("init_db", "create_admin")
def test_create_admin(test_app: Flask, get_objects: GetObjects) -> None:
    """Test commands called when invoking ``flask create admin``.

    :param test_app: Test application.
    :param get_objects: Get test objects with db model attributes.
    """
    u_o = get_objects.user(0)
    with test_app.app_context():
        u_q = User.query.get(1)
        assert u_q.email == u_o[0].email
        assert u_q.check_password(u_o[0].password)


@pytest.mark.usefixtures("init_db")
def test_create_user_cli(
    test_app: Flask,
    runner: FlaskCliRunner,
    get_objects: GetObjects,
    patch_getpass: PatchGetpassType,
) -> None:
    """Test commands called when invoking ``flask create user``.

    :param test_app: Test application.
    :param runner: Test application cli.
    :param get_objects: Get test objects with db model attributes.
    :param patch_getpass: Patch ``getpass`` password module.
    """
    u_o = get_objects.user(1)
    patch_getpass([u_o[1].password, u_o[1].password])
    response = runner.invoke(
        args=["create", "user"], input=f"{u_o[1].username}\n{u_o[1].email}\n"
    )
    assert "user successfully created" in response.output
    with test_app.app_context():
        u_q = User.query.get(1)
        assert u_q.email == u_o[1].email
        assert u_q.check_password(u_o[1].password)


@pytest.mark.parametrize(
    "username,email,passwords,expected",
    [
        (
            user_username[1],
            user_email[2],
            [user_password[1], user_password[2]],
            "username is taken",
        ),
        (
            user_username[2],
            user_email[1],
            [user_password[1], user_password[1]],
            "already registered",
        ),
        (
            user_username[2],
            user_email[2],
            [user_password[1], user_password[2]],
            "passwords do not match",
        ),
    ],
    ids=["username", "email", "pass"],
)
@pytest.mark.usefixtures("init_db")
def test_create_user_fail(
    runner: FlaskCliRunner,
    routes: Routes,
    authorize_user: AuthorizeUserFixtureType,
    get_objects: GetObjects,
    patch_getpass: PatchGetpassType,
    username: str,
    email: str,
    passwords: t.List[str],
    expected: str,
) -> None:
    """Test creation of a new user that fails.

    :param runner: Test application cli.
    :param routes: Work with application routes.
    :param authorize_user: Authorize existing user.
    :param get_objects: Get test objects with db model attributes.
    :param patch_getpass: Patch ``getpass`` password module.
    :param username: The test user username.
    :param email: The test user email.
    :param passwords: Password and password confirmation.
    :param expected: Expected result.
    """
    u_o = get_objects.user(1)
    routes.auth.register(u_o[1])
    authorize_user(1)
    patch_getpass(passwords)
    response = runner.invoke(
        args=["create", "user"], input=f"{username}\n{email}\n"
    )
    assert expected in response.output


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize(
    "route", ["/post/create", "/post/1/update", "/post/1/delete"]
)
def test_admin_required(
    client: FlaskClient, routes: Routes, route: str
) -> None:
    """Test requirement that admin user be logged in to post.

    An admin user must be logged in to access the "create", "update",
    and "delete" views.

    The logged-in user must be the author of the post to access the
    update and delete views, otherwise a ``403 Forbidden`` status is
    returned.

    :param client: Test application client.
    :param routes: Work with application routes.
    :param route: Parametrized route path.
    """
    routes.auth.register_index(1)
    routes.auth.login_index(1)
    assert client.post(route).status_code == 401


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize(
    "username,email,expected",
    [
        (user_username[1], user_email[2], b"Username is taken"),
        (user_username[2], user_email[1], b"already registered"),
    ],
    ids=["username", "email"],
)
def test_register_invalid_fields(
    routes: Routes,
    get_objects: GetObjects,
    username: str,
    email: str,
    expected: str,
) -> None:
    """Test different invalid input and error messages.

    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    :param username: The test user username.
    :param email: The test user email.
    :param expected: Expected result.
    """
    u_o = get_objects.user(1)
    routes.auth.register_index(1)
    u_o[1].username = username
    u_o[1].email = email
    response = routes.auth.register(u_o[1])
    assert expected in response.data


@pytest.mark.usefixtures("init_db")
def test_confirmation_email(test_app: Flask, routes: Routes) -> None:
    """Test user is moved from confirmed as False to True.

    :param test_app: Test application.
    :param routes: Work with application routes.
    """
    with mail.record_messages() as outbox:
        routes.auth.register_index(1)
        response = routes.auth.get("/unconfirmed")

    with test_app.app_context():
        assert b"A confirmation email has been sent." in response.data
        assert User.query.get(1).confirmed is False
        routes.auth.follow_token(outbox[0].html)
        assert User.query.get(1).confirmed is True


@pytest.mark.usefixtures("init_db")
def test_confirmation_email_confirmed(routes: Routes) -> None:
    """Test user redirected when already confirmed.

    :param routes: Work with application routes.
    """
    with mail.record_messages() as outbox:
        routes.auth.register_index(1, confirm=True)

    response = routes.auth.follow_token(outbox[0].html)
    assert b"Account already confirmed. Please login." in response.data


@pytest.mark.usefixtures("init_db")
def test_confirmation_email_expired(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    routes: Routes,
) -> None:
    """Test user denied when confirmation is expired. Allow resend.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param client: Test application client.
    :param routes: Work with application routes.
    """
    with mail.record_messages() as outbox:
        routes.auth.register_index(1)

    route = routes.auth.parse_href(outbox[0].html)
    token = route.replace("https://localhost/auth", "")
    serializer = URLSafeTimedSerializer(test_app.config["SECRET_KEY"])
    confirm_token = functools.partial(
        serializer.loads,
        token,
        salt=test_app.config["SECURITY_PASSWORD_SALT"],
        max_age=1,
    )
    monkeypatch.setattr(
        "app.routes.redirect.confirm_token", lambda _: confirm_token()
    )
    response = client.get(route, follow_redirects=True)
    assert INVALID_OR_EXPIRED in response.data


@pytest.mark.usefixtures("init_db")
def test_login_confirmed(
    client: FlaskClient, routes: Routes, get_objects: GetObjects
) -> None:
    """Test login functionality once user is verified.

    :param client: Flask client testing helper.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    """
    u_o = get_objects.user(1)
    routes.auth.register_index(1, confirm=True)
    response = routes.auth.login_index(1)
    assert response.headers["Location"] == "https://localhost/"
    with client:
        client.get("/")
        assert current_user.username == u_o[1].username


@pytest.mark.usefixtures("init_db")
def test_confirmation_email_resend(
    client: FlaskClient, routes: Routes
) -> None:
    """Test user receives email when requesting resend.

    :param client: Test application client.
    :param routes: Work with application routes.
    """
    routes.auth.register_index(1)
    response = client.get("/redirect/resend", follow_redirects=True)
    assert b"A new confirmation email has been sent." in response.data


@pytest.mark.usefixtures("init_db")
def test_request_password_reset_email(
    routes: Routes, get_objects: GetObjects, add_test_objects: AddTestObjects
) -> None:
    """Test that the correct email is sent to user for password reset.

    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    :param add_test_objects: Add test objects to test database.
    """
    u_o = get_objects.user(1)
    add_test_objects.add_test_users(u_o[1])
    with mail.record_messages() as outbox:
        routes.auth.request_password_reset(1)

    response = routes.auth.follow_token(outbox[0].html)
    assert b"Reset Password" in response.data
    assert b"Please enter your new password" in response.data


@pytest.mark.usefixtures("init_db")
def test_bad_token(monkeypatch: pytest.MonkeyPatch, routes: Routes) -> None:
    """Test user denied when jwt for resetting password is expired.

    :param monkeypatch: Mock patch environment and attributes.
    :param routes: Work with application routes.
    """
    routes.auth.register_index(1)
    with mail.record_messages() as outbox:
        monkeypatch.setattr(
            "app.routes.auth.generate_reset_password_token",
            lambda *_, **__: "bad_token",
        )
        routes.auth.request_password_reset(1)

    response = routes.auth.follow_token(outbox[0].html)
    assert INVALID_OR_EXPIRED in response.data


@pytest.mark.usefixtures("init_db")
def test_email_does_not_exist(routes: Routes) -> None:
    """Test user notified when email does not exist for password reset.

    :param routes: Work with application routes.
    """
    response = routes.auth.request_password_reset(1)
    assert b"An account with that email address doesn't exist" in response.data


@pytest.mark.usefixtures("init_db")
def test_redundant_token(routes: Routes) -> None:
    """Test user notified that them being logged in has voided token.

    :param routes: Work with application routes.
    """
    routes.auth.register_index(1)
    with mail.record_messages() as outbox:
        routes.auth.request_password_reset(1)

    routes.auth.login_index(1)
    response = routes.auth.follow_token(outbox[0].html)
    assert INVALID_OR_EXPIRED in response.data


@pytest.mark.usefixtures("init_db")
def test_reset_password(
    test_app: Flask,
    routes: Routes,
    get_objects: GetObjects,
    add_test_objects: AddTestObjects,
) -> None:
    """Test the password reset process.

    :param test_app: Test application.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    :param add_test_objects: Add test objects to test database.
    """
    u_o = get_objects.user(2)
    add_test_objects.add_test_users(u_o[1])
    with mail.record_messages() as outbox:
        routes.auth.request_password_reset(1)

    with test_app.app_context():
        u_q = User.query.get(1)
        assert u_q.check_password(u_o[1].password)
        routes.auth.reset_password(2, outbox[0].html)
        assert not u_q.check_password(u_o[1].password)
        assert u_q.check_password(u_o[2].password)


@pytest.mark.parametrize("use_tls,secure", [(False, None), (True, ())])
def test_get_smtp_handler(
    monkeypatch: pytest.MonkeyPatch,
    use_tls: bool,
    secure: t.Tuple[None] | None,
) -> None:
    """Test correct values passed to ``SMTPHandler``.

    :param monkeypatch: Mock patch environment and attributes.
    :param use_tls: True or False.
    :param secure: Tuple if TLS True, None if TLS False.
    """
    app = Recorder()
    app.config = {}  # type: ignore
    app.debug = False  # type: ignore
    app.config["MAIL_SERVER"] = MAIL_SERVER  # type: ignore
    app.config["MAIL_USERNAME"] = MAIL_USERNAME  # type: ignore
    app.config["MAIL_PASSWORD"] = MAIL_PASSWORD  # type: ignore
    app.config["MAIL_USE_TLS"] = use_tls  # type: ignore
    app.config["MAIL_PORT"] = MAIL_PORT  # type: ignore
    app.config["ADMINS"] = [MAIL_USERNAME]  # type: ignore
    app.logger = Recorder()  # type: ignore
    app.logger.handlers = []  # type: ignore
    app.logger.addHandler = app.logger.handlers.append  # type: ignore
    state = Recorder()
    state.loglevel = 0  # type: ignore
    state.setLevel = lambda x: x  # type: ignore
    state.setFormatter = lambda x: x  # type: ignore
    state.formatter = logging.Formatter()  # type: ignore
    monkeypatch.setattr("app.log.SMTPHandler", state)
    smtp_handler(app)  # type: ignore
    assert state in app.logger.handlers  # type: ignore
    kwargs = state.kwargs
    assert kwargs["mailhost"] == (MAIL_SERVER, MAIL_PORT)
    assert kwargs["fromaddr"] == f"no-reply@{MAIL_SERVER}"
    assert kwargs["toaddrs"] == [MAIL_USERNAME]
    assert kwargs["credentials"] == (MAIL_USERNAME, MAIL_PASSWORD)
    assert kwargs["secure"] == secure


@pytest.mark.usefixtures("init_db")
def test_profile_page(routes: Routes) -> None:
    """Test response when visiting profile page of existing user.

    :param routes: Work with application routes.
    """
    routes.auth.register_index(1)
    response = routes.profile.user(1)
    assert b'src="https://gravatar.com/avatar/' in response.data


# noinspection DuplicatedCode
@pytest.mark.usefixtures("init_db")
def test_post_page(
    routes: Routes,
    get_objects: GetObjects,
    authorize_user: AuthorizeUserFixtureType,
) -> None:
    """Test for correct contents in post page response.

    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    :param authorize_user: Authorize existing user.
    """
    p_o = get_objects.post(1)
    routes.auth.register_index(1)
    authorize_user(1)
    routes.auth.login_index(1)
    routes.posts.create(1)
    response = routes.posts.read(1)
    assert p_o[1].title.encode() in response.data
    assert p_o[1].body.encode() in response.data


@pytest.mark.usefixtures("init_db")
def test_edit_profile(routes: Routes, get_objects: GetObjects) -> None:
    """Test edit profile page.

    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    """
    u_o = get_objects.user(2)
    routes.auth.register_index(1, confirm=True)
    routes.auth.login_index(1)
    response = routes.user.get("/profile/edit")
    assert b"Edit Profile" in response.data
    assert b"Profile" in response.data
    assert b"Logout" in response.data
    assert b"Edit Profile" in response.data
    assert b"About me" in response.data
    assert u_o[1].username.encode() in response.data
    response = routes.user.edit(
        u_o[2].username, "testing about me", follow_redirects=True
    )
    assert u_o[1].username.encode() not in response.data
    assert u_o[2].username.encode() in response.data
    assert b"testing about me" in response.data


@pytest.mark.usefixtures("init_db")
def test_unconfirmed(routes: Routes) -> None:
    """Test when unconfirmed user tries to enter restricted view.

    :param routes: Work with application routes.
    """
    routes.auth.register_index(1)
    routes.auth.login_index(1)
    response = routes.user.get("/profile/edit", follow_redirects=True)
    assert b"Account Verification Pending" in response.data


@pytest.mark.usefixtures("init_db")
def test_follow(
    test_app: Flask, routes: Routes, get_objects: GetObjects
) -> None:
    """Test functionality of user follows.

    :param test_app: Test application.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    """
    u_o = get_objects.user(2)
    routes.auth.register_index(1, confirm=True)
    routes.auth.register_index(2)
    with test_app.app_context():
        u_q_1 = User.query.filter_by(username=u_o[1].username).first()
        u_q_2 = User.query.filter_by(username=u_o[2].username).first()
        assert u_q_1.followed.all() == []
        assert u_q_1.followers.all() == []
        routes.auth.login_index(1)
        routes.redirect.follow(2)
        assert u_q_1.is_following(u_q_2)
        assert u_q_1.followed.count() == 1
        assert u_q_1.followed.first().username == u_o[2].username
        assert u_q_2.followers.count() == 1
        assert u_q_2.followers.first().username == u_o[1].username
        routes.redirect.unfollow(2)
        assert not u_q_1.is_following(u_q_2)
        assert u_q_1.followed.count() == 0
        assert u_q_2.followers.count() == 0


# noinspection DuplicatedCode
@pytest.mark.usefixtures("init_db")
def test_follow_posts(
    test_app: Flask,
    routes: Routes,
    get_objects: GetObjects,
    authorize_user: AuthorizeUserFixtureType,
) -> None:
    """Test functionality of post follows.

    :param test_app: Test application.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    :param authorize_user: Authorize existing user.
    """
    u_o = get_objects.user(4)
    p_o = get_objects.post(4)
    with test_app.app_context():
        routes.auth.register_index(1, confirm=True)
        routes.auth.register_index(2, confirm=True)
        routes.auth.register_index(3, confirm=True)
        routes.auth.register_index(4)
        authorize_user(1)
        authorize_user(2)
        authorize_user(3)
        authorize_user(4)

        routes.auth.login_index(1)
        routes.posts.create(1)
        routes.redirect.follow(2)
        routes.redirect.follow(4)
        routes.auth.logout()

        routes.auth.login_index(2)
        routes.posts.create(2)
        routes.redirect.follow(3)
        routes.auth.logout()

        routes.auth.login_index(3)
        routes.posts.create(3)
        routes.redirect.follow(4)
        routes.auth.logout()

        routes.auth.login_index(4)
        routes.posts.create(4)
        routes.auth.logout()

        u_q_1 = User.query.filter_by(username=u_o[1].username).first()
        u_q_2 = User.query.filter_by(username=u_o[2].username).first()
        u_q_3 = User.query.filter_by(username=u_o[3].username).first()
        u_q_4 = User.query.filter_by(username=u_o[4].username).first()
        p_q_1 = Post.query.filter_by(title=p_o[1].title).first()
        p_q_2 = Post.query.filter_by(title=p_o[2].title).first()
        p_q_3 = Post.query.filter_by(title=p_o[3].title).first()
        p_q_4 = Post.query.filter_by(title=p_o[4].title).first()

        # check the followed posts of each user
        followed_1 = u_q_1.followed_posts().all()
        followed_2 = u_q_2.followed_posts().all()
        followed_3 = u_q_3.followed_posts().all()
        followed_4 = u_q_4.followed_posts().all()
        assert followed_1 == [p_q_4, p_q_2, p_q_1]
        assert followed_2 == [p_q_3, p_q_2]
        assert followed_3 == [p_q_4, p_q_3]
        assert followed_4 == [p_q_4]


@pytest.mark.usefixtures("init_db")
def test_post_follow_unfollow_routes(
    routes: Routes, get_objects: GetObjects
) -> None:
    """Test ``POST`` request to follow and unfollow a user.

    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    """
    # create and log in test users
    u_o = get_objects.user(2)
    routes.auth.register_index(1, confirm=True)
    routes.auth.register_index(2, confirm=True)
    routes.auth.login_index(1)
    routes.auth.login_index(2)
    response = routes.redirect.follow(2, follow_redirects=True)
    assert f"You are now following {u_o[2].username}".encode() in response.data
    response = routes.redirect.unfollow(2, follow_redirects=True)
    assert (
        f"You are no longer following {u_o[2].username}".encode()
        in response.data
    )


@pytest.mark.usefixtures("init_db")
def test_send_message(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    routes: Routes,
    get_objects: GetObjects,
) -> None:
    """Test sending of personal messages from one user to another.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param client: Test application client.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    """
    u_o = get_objects.user(2)
    routes.auth.register_index(1, confirm=True)
    routes.auth.register_index(2, confirm=True)
    routes.auth.login_index(1)
    response = routes.user.send_message(2, follow_redirects=True)
    assert b"Your message has been sent." in response.data
    response = routes.user.get(f"/send_message/{u_o[2].username}")
    assert f"Send Message to {u_o[2].username}".encode() in response.data
    routes.auth.logout()
    routes.auth.login_index(2)

    # test icon span
    monkeypatch.setenv("NAVBAR_ICONS", "1")
    config.init_app(test_app)

    # ensure the badge (<span> tag) is displayed when there are messages
    # held for the user
    response = client.get("/")
    assert b"nav-link btn-lg btn-link" in response.data
    assert b'href="/user/messages' in response.data
    assert b'title="Messages"' in response.data
    assert b'class="bi-bell"' in response.data
    assert b"badge badge-pill badge-primary badge-notify" in response.data
    assert b'id="message_count' in response.data
    # for reliable testing ensure navbar not set to display icons
    monkeypatch.setenv("NAVBAR_ICONS", "0")
    config.init_app(test_app)

    # ensure the badge (<span> tag) is displayed when there are messages
    # held for the user
    response = client.get("/")
    assert b'nav-link" href="/user/messages' in response.data
    assert b'title="Messages' in response.data
    assert b"Messages" in response.data
    assert b"badge" in response.data
    assert b'id="message_count' in response.data
    response = routes.user.notifications()
    obj = response.json[0]  # type: ignore
    assert "data" in obj
    assert "name" in obj
    assert "timestamp" in obj
    assert 1 in obj.values()
    assert "unread_message_count" in obj.values()

    # entering this view will confirm that the messages have been
    # viewed and there will be no badge with a count displayed
    response = routes.user.messages()
    assert u_o[2].message.encode() in response.data


@pytest.mark.usefixtures("init_db")
def test_export_post_is_job(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    routes: Routes,
    get_objects: GetObjects,
) -> None:
    """Test export post function when a job already exists: is not None.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param client: Test application client.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    """
    u_o = get_objects.user(1)
    routes.auth.register_index(1, confirm=True)
    routes.auth.login_index(1)
    routes.posts.create(1)
    app_current_user = Recorder()
    app_current_user.is_authenticated = lambda: True  # type: ignore
    app_current_user.get_task_in_progress = lambda _: 1  # type: ignore
    app_current_user.username = u_o[1].username  # type: ignore
    with test_app.app_context():
        app_current_user.post = Post.query.get(1)  # type: ignore
        monkeypatch.setattr(
            "app.routes.redirect.current_user", app_current_user
        )
        response = client.get("/redirect/export_posts", follow_redirects=True)

    assert b"An export task is already in progress" in response.data


# noinspection DuplicatedCode
@pytest.mark.usefixtures("init_db")
def test_export_post(test_app: Flask, routes: Routes) -> None:
    """Test export post function when a job does not exist: is None.

    :param test_app: Test application.
    :param routes: Work with application routes.
    """
    routes.auth.register_index(1, confirm=True)
    routes.redirect.add_export_posts_task(TASK_ID)
    with test_app.app_context():
        task = Task.query.get(TASK_ID)
        assert task.id == TASK_ID
        assert task.user_id == 1
        assert task.complete is False
        assert task.description == "Exporting posts..."
        assert task.name == "export_posts"


@pytest.mark.usefixtures("init_db")
def test_get_tasks_in_progress_no_task(
    monkeypatch: pytest.MonkeyPatch, client: FlaskClient, routes: Routes
) -> None:
    """Test getting of a task when one does not exist.

    :param monkeypatch: Mock patch environment and attributes.
    :param client: Test application client.
    :param routes: Work with application routes.
    """
    routes.auth.register_index(1)
    routes.auth.login_index(1)
    monkeypatch.setattr(APP_MODELS_JOB_FETCH, lambda *_, **__: None)
    response = client.get("/")
    assert b"100" in response.data


# noinspection DuplicatedCode
@pytest.mark.usefixtures("init_db")
def test_get_tasks_in_progress(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    routes: Routes,
) -> None:
    """Test getting of a task when there is a task in the database.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param client: Test application client.
    :param routes: Work with application routes.
    """
    rq_job = Recorder()
    rq_job.meta = {"progress": MISC_PROGRESS_INT}  # type: ignore
    monkeypatch.setattr(APP_MODELS_JOB_FETCH, lambda *_, **__: rq_job)
    routes.auth.register_index(1, confirm=True)
    routes.auth.login_index(1)
    routes.redirect.add_export_posts_task(TASK_ID)
    with test_app.app_context():
        assert Task.query.get(TASK_ID) is not None

    response = client.get("/")
    assert str(MISC_PROGRESS_INT).encode() in response.data


# noinspection DuplicatedCode
@pytest.mark.usefixtures("init_db")
def test_get_tasks_in_progress_error_raised(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    routes: Routes,
    get_objects: GetObjects,
) -> None:
    """Test getting of a task when an error is raised: 100%, complete.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param client: Test application client.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    """

    def _fetch(*_: t.Any, **__: t.Any) -> None:
        raise RedisError("test Redis error")

    monkeypatch.setattr(APP_MODELS_JOB_FETCH, _fetch)
    u_o = get_objects.user(1)
    routes.auth.register(u_o[1], confirm=True)
    routes.auth.login(u_o[1])
    routes.redirect.add_export_posts_task(TASK_ID)
    with test_app.app_context():
        assert Task.query.get(TASK_ID) is not None

    response = client.get("/")
    assert b"100" in response.data


# noinspection DuplicatedCode
@pytest.mark.flaky(max_runs=5)
@pytest.mark.usefixtures("init_db")
def test_export_posts(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    routes: Routes,
    get_objects: GetObjects,
    authorize_user: AuthorizeUserFixtureType,
) -> None:
    """Test data as sent to user when post export requested.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    :param authorize_user: Authorize existing user.
    """
    # this needs to imported *after* `monkeypatch.setenv` has patched
    # the environment
    import app.utils.tasks

    # faster than waiting for `mail.record_messages` to sync
    # catch `Message` object passed to `mail.send`
    monkeypatch.setattr("app.utils.tasks.time.sleep", lambda _: None)
    u_o = get_objects.user(1)
    p_o = get_objects.post(1)
    routes.auth.register(u_o[1], confirm=True)
    authorize_user(1)
    routes.auth.login_index(1)
    routes.posts.create(1)
    routes.redirect.add_export_posts_task(TASK_ID)
    job = Recorder()
    job.meta = {}  # type: ignore
    job.save_meta = Recorder()  # type: ignore
    job.get_id = lambda: TASK_ID  # type: ignore
    monkeypatch.setattr("app.utils.tasks.get_current_job", lambda: job)
    with mail.record_messages() as outbox:
        app.utils.tasks.export_posts(1)
        with test_app.app_context():
            p_q = Post.query.get(1)

        post_obj = [
            dict(
                body=p_o[1].body,
                created=str(p_q.created),
                edited="None",
                id="1",
                title=p_o[1].title,
                user_id="1",
            )
        ]
        recv = outbox[0]
        attachment = recv.attachments[0]
        assert recv.subject == f"[JSS]: Posts by {u_o[1].username}"
        assert recv.recipients == [u_o[1].email]
        assert u_o[1].username in recv.html
        assert "Please find attached the archive of your posts" in recv.html
        assert attachment.filename == "posts.json"
        assert attachment.content_type == "application/json"
        assert attachment.data == json.dumps(
            {"posts": post_obj}, indent=4, sort_keys=True
        )


@pytest.mark.usefixtures("init_db")
def test_export_posts_err(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test data as sent to user when post export requested with error.

    Test except and clean-up.

    :param monkeypatch: Mock patch environment and attributes.
    """
    # this needs to imported *after* `monkeypatch.setenv` has patched
    # the environment
    import app.utils.tasks

    monkeypatch.setattr(
        "app.utils.tasks._app.logger.error", lambda *_, **__: None
    )

    def _set_task_progress(progress: int) -> None:
        # fail when not setting func to 100
        assert progress == 100

    monkeypatch.setattr(
        "app.utils.tasks._set_task_progress", _set_task_progress
    )
    app.utils.tasks.export_posts(1)


@pytest.mark.usefixtures("init_db")
def test_versions(
    routes: Routes, authorize_user: AuthorizeUserFixtureType
) -> None:
    """Test versioning of posts route.

    :param routes: Work with application routes.
    :param authorize_user: Authorize existing user.
    """
    routes.auth.register_index(1)
    authorize_user(1)
    routes.auth.login_index(1)
    routes.posts.create(1)
    routes.posts.update(1, 1)
    assert b"v1" in routes.posts.read(1, 0).data
    assert b"v2" in routes.posts.read(1, 1).data
    assert routes.posts.read(1, 2).status_code == 404


@pytest.mark.usefixtures("init_db", "create_admin")
def test_admin_access_control(routes: Routes) -> None:
    """Test access to admin console restricted to admin user.

    :param routes: Work with application routes.
    """
    routes.auth.register_index(1)
    routes.auth.login_index(0)
    assert routes.admin.get(follow_redirects=True).status_code == 200
    assert routes.admin.users(follow_redirects=True).status_code == 200
    routes.auth.logout()
    routes.auth.login_index(1)
    assert routes.admin.get(follow_redirects=True).status_code == 401
    assert routes.admin.users(follow_redirects=True).status_code == 403


@pytest.mark.usefixtures("init_db")
def test_admin_access_without_login(routes: Routes) -> None:
    """Asserts that the ``AnonymousUserMixin`` error will not be raised.

    This commit fixes the following error causing app to crash if user
    is not logged in:

        AttributeError:
        'AnonymousUserMixin' object has no attribute 'admin'

    :param routes: Work with application routes.
    """
    assert routes.admin.get(follow_redirects=True).status_code == 401
    assert routes.admin.users(follow_redirects=True).status_code == 403


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize(
    "method,data,bad_route",
    [
        ("get", {}, "profile/noname"),
        ("post", {}, "follow/noname"),
        ("post", {}, "unfollow/noname"),
        ("post", {"message": "testing"}, "send_message/noname"),
    ],
    ids=["profile", "follow", "unfollow", "send_message"],
)
def test_inspect_profile_no_user(
    client: FlaskClient,
    routes: Routes,
    method: str,
    data: t.Dict[str, str],
    bad_route: str,
) -> None:
    """Assert that unhandled error is not raised for user routes.

    This commit fixes the following error:

        AttributeError: 'NoneType' object has no attribute 'posts'

    If a non-existing user is searched, prior to this commit, the route
    will use methods belonging to the user (assigned None).

    Prefer to handle the exception and return a ``404: Not Found`` error
    instead.

    e.g.  Use ``User.query.filter_by(username=username).first_or_404()``
    instead of ``User.query.filter_by(username=username).first()``

    :param client: Test application client.
    :param routes: Work with application routes.
    :param method: Method for interacting with route.
    :param data: Data to write to form.
    :param bad_route: Route containing reference to non-existing u_o.
    """
    routes.auth.login_index(1)
    assert getattr(client, method)(bad_route, data=data).status_code == 404


@pytest.mark.usefixtures("init_db")
def test_user_name_change_accessible(
    test_app: Flask, routes: Routes, get_objects: GetObjects
) -> None:
    """Test that even after name-change user is accessible by old name.

    Only valid if the old name has not already been adopted by someone
    else.

    :param test_app: Test application.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    """
    u_o = get_objects.user(3)
    routes.auth.register_index(1, confirm=True)
    routes.auth.login_index(1)

    with test_app.app_context():
        # assert that user's profile is available via profile route
        u_q = User.resolve_all_names(u_o[1].username)
        assert u_q.id == 1

        response = routes.profile.user(1)
        assert u_o[1].username.encode() in response.data

        # assert that name change is successful
        routes.user.edit(u_o[2].username)
        u_q = User.resolve_all_names(u_o[2].username)
        assert u_q.id == 1

        response = routes.profile.user(1)
        assert response.status_code != 404
        assert u_o[2].username.encode() in response.data

        # assert that user can be referenced by their old username
        # they're new name shows up in their profile page
        # the old username is still attached to the same user id
        u_q = User.resolve_all_names(u_o[1].username)
        assert u_q.id == 1

        response = routes.profile.user(1)
        assert u_o[2].username.encode() in response.data

        # assert that od name is now a valid choice for a new user
        u_o[2].username = u_o[1].username
        routes.auth.register(u_o[2], confirm=True)
        routes.auth.login(u_o[2])

        # assert that user's profile is available via profile route
        u_q = User.resolve_all_names(u_o[1].username)
        assert u_q.id == 2

        response = routes.profile.user(1)
        assert u_o[1].username.encode() in response.data

        # assert that name change is successful for second user
        routes.user.edit(u_o[3].username)
        u_q = User.resolve_all_names(u_o[3].username)
        assert u_q.id == 2

        response = routes.profile.user(1)
        assert u_o[3].username.encode() in response.data

        # assert that the latest user can be referenced by the old username
        # they're new name shows up in their profile page
        # the old username is still attached to the same user id
        u_q = User.resolve_all_names(u_o[1].username)
        assert u_q.id == 2

        response = routes.profile.user(1)
        assert response.status_code != 404
        assert u_o[3].username.encode() in response.data


@pytest.mark.usefixtures("init_db")
def test_reserved_usernames(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    routes: Routes,
    get_objects: GetObjects,
) -> None:
    """Test that reserved names behave as taken names would in register.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    """
    u_o = get_objects.user(2)
    monkeypatch.setenv(
        "RESERVED_USERNAMES", f"{u_o[1].username},{u_o[2].username}"
    )
    config.init_app(test_app)
    assert test_app.config["RESERVED_USERNAMES"] == [
        u_o[1].username,
        u_o[2].username,
    ]
    response = routes.auth.register_index(1)
    assert b"Username is taken" in response.data
    response = routes.auth.register_index(2)
    assert b"Username is taken" in response.data


# noinspection DuplicatedCode
@pytest.mark.usefixtures("init_db")
def test_versions_update(
    routes: Routes,
    get_objects: GetObjects,
    authorize_user: AuthorizeUserFixtureType,
) -> None:
    """Test versioning of posts route when passing revision to update.

    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    :param authorize_user: Authorize existing user.
    """
    p_o = get_objects.post(2)
    routes.auth.register_index(1)
    authorize_user(1)
    routes.auth.login_index(1)
    routes.posts.create(1)
    routes.posts.update(2, 1)
    response = routes.posts.read(1, 0)
    assert p_o[1].title.encode() in response.data
    assert p_o[1].body.encode() in response.data


@pytest.mark.usefixtures("init_db")
def test_versioning_handle_index_error(routes: Routes) -> None:
    """Test versioning route when passing to large a revision to update.

    :param routes: Work with application routes.
    """
    routes.auth.register_index(1)
    routes.posts.create(1)
    routes.auth.login_index(1)
    assert routes.posts.read(1, 1).status_code == 404


def test_config_copyright(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, test_app: Flask
) -> None:
    """Test parsing of metadata from project root.

    :param tmp_path: Create and return temporary ``Path`` object.
    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    """
    monkeypatch.setattr("os.environ", {})
    license_file = tmp_path / "LICENSE"
    pyproject_toml = tmp_path / "pyproject.toml"
    license_file.write_text(LICENSE, encoding="utf-8")
    pyproject_toml.write_text(PYPROJECT_TOML, encoding="utf-8")
    monkeypatch.setenv("LICENSE", str(license_file))
    monkeypatch.setenv("PYPROJECT_TOML", str(pyproject_toml))
    config.init_app(test_app)
    assert test_app.config["LICENSE"] == license_file
    assert test_app.config["COPYRIGHT_YEAR"] == COPYRIGHT_YEAR
    assert test_app.config["COPYRIGHT_AUTHOR"] == COPYRIGHT_AUTHOR
    assert test_app.config["COPYRIGHT_EMAIL"] == COPYRIGHT_EMAIL


@pytest.mark.usefixtures("init_db")
def test_navbar_home_config_switch(
    monkeypatch: pytest.MonkeyPatch, test_app: Flask, client: FlaskClient
) -> None:
    """Test that the navbar Home link appropriately switches on and off.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param client: Test application client.
    """
    # with `NAVBAR_HOME` set to False
    monkeypatch.setenv("NAVBAR_HOME", "0")
    config.init_app(test_app)
    assert test_app.config["NAVBAR_HOME"] is False
    response = client.get("/")
    assert b"Home" not in response.data

    # with `NAVBAR_HOME` set to True
    monkeypatch.setenv("NAVBAR_HOME", "1")
    config.init_app(test_app)
    assert test_app.config["NAVBAR_HOME"] is True
    response = client.get("/")
    assert b"Home" in response.data


@pytest.mark.parametrize(
    "env,expected",
    [
        ("0", b'<div class="list-group list-group-horizontal">'),
        ("1", b'<ul class="dropdown-menu dropdown-menu-right">'),
    ],
    ids=["disabled", "enabled"],
)
@pytest.mark.usefixtures("init_db")
def test_navbar_user_dropdown_config_switch(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    routes: Routes,
    env: str,
    expected: bytes,
) -> None:
    """Test that the user dropdown appropriately switches on and off.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param client: Test application client.
    :param routes: Work with application routes.
    :param env: Value for ``NAVBAR_USER_DROPDOWN``.
    :param expected: Expected result.
    """
    routes.auth.register_index(1)
    routes.auth.login_index(1)
    monkeypatch.setenv("NAVBAR_USER_DROPDOWN", env)
    config.init_app(test_app)
    response = client.get("/")
    assert expected in response.data


def test_all_routes_covered(test_app: Flask) -> None:
    """Test all routes that need to be tested will be.

    :param test_app: Test application.
    """
    ignore = ["/admin/*", "/static/*", "/bootstrap/*"]
    exception = ["/admin/"]
    filter_covered = [
        r.rule
        for r in test_app.url_map.iter_rules()
        if not any(fnmatch.fnmatch(r.rule, i) for i in ignore)
        or r.rule in exception
    ]
    assert "/admin/admin_notification/ajax/lookup/" not in filter_covered
    assert "/admin/" in filter_covered
    assert all(r in COVERED_ROUTES for r in filter_covered)


@pytest.mark.usefixtures("init_db", "init_static")
@pytest.mark.parametrize(
    "code,test_routes", STATUS_CODE_TO_ROUTE_DEFAULT, ids=[200, 401, 405]
)
def test_static_route_default(
    client: FlaskClient,
    routes: Routes,
    get_objects: GetObjects,
    authorize_user: AuthorizeUserFixtureType,
    interpolate_routes: InterpolateRoutesType,
    code: int,
    test_routes: t.List[str],
) -> None:
    """Specifically test all status codes of routes.

    :param client: Test application client.
    :param routes: Work with application routes.
    :param get_objects: Get test objects with db model attributes.
    :param authorize_user: Authorize existing user.
    :param interpolate_routes: Interpolate route vars with test values.
    :param code: Status code expected.
    :param test_routes: List of routes with expected status code.
    """
    u_o = get_objects.user(1)
    routes.auth.register_index(1)
    authorize_user(1)
    routes.auth.login_index(1)
    routes.posts.create(1)
    routes.auth.logout()
    interpolate_routes(test_routes, 1, 0, u_o[1].username)
    assert all(
        client.get(r, follow_redirects=True).status_code == code
        for r in test_routes
    )


@pytest.mark.parametrize(
    "attr,obj,expected_repr",
    [
        (
            "app.utils.register.RegisterContext",
            RegisterContext,
            "<RegisterContext {}>",
        ),
        (
            "app.utils.csp.ContentSecurityPolicy",
            ContentSecurityPolicy,
            "<ContentSecurityPolicy {}>",
        ),
    ],
    ids=["register", "csp"],
)
def test_mutable_mapping_dunders(
    monkeypatch: pytest.MonkeyPatch,
    attr: str,
    obj: t.Type[t.MutableMapping],
    expected_repr: str,
) -> None:
    """Test ``MutableMapping`` dunder methods (coverage).

    :param monkeypatch: Mock patch environment and attributes.
    :param attr: Attribute to monkeypatch.
    :param obj: Object to monkeypatch attribute with.
    :param expected_repr: Expected repr result.
    """
    monkeypatch.setattr(attr, obj)
    key = "key"
    value = "value"
    self = obj()
    assert repr(self) == expected_repr
    assert key not in self
    assert len(self) == 0
    self[key] = value
    assert key in self
    assert len(self) == 1
    assert self[key] == value
    del self[key]
    assert key not in self
    assert len(self) == 0


def test_register_text(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test text is registered.

    :param monkeypatch: Mock patch environment and attributes.
    """
    monkeypatch.setattr("app.utils.register.RegisterContext", RegisterContext)
    text = RegisterContext("dom_text")
    assert repr(text) == "<RegisterContext {}>"
    test_str = "Title"

    @text.register
    def registered_text() -> str:
        return test_str

    registered = RegisterContext.registered()
    assert registered["dom_text_registered_text"]() == test_str


@pytest.mark.usefixtures("init_db")
def test_version_dropdown(
    client: FlaskClient,
    routes: Routes,
    authorize_user: AuthorizeUserFixtureType,
) -> None:
    """Test version dropdown.

    Test all 3 variations of unordered list items.

    :param client: Test application client.
    :param routes: Work with application routes.
    :param authorize_user: Authorize existing user.
    """
    routes.auth.register_index(1)
    authorize_user(1)
    routes.auth.login_index(1)
    routes.posts.create(1)

    # create 3 versions (2 other, apart from the original) for all
    # naming branches
    routes.posts.update(2, 1)
    routes.posts.update(3, 1)

    response = client.get("/")
    assert b'<a href="/post/1?revision=0">' in response.data
    assert b"v1" in response.data
    assert b'<a href="/post/1?revision=1">' in response.data
    assert b"v2: Previous revision" in response.data
    assert b"current-version-anchor" in response.data
    assert b'href="/post/1?revision=2' in response.data
    assert b"v3: This revision" in response.data


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize(
    "route,test_object,prop,method,user_do,user_view",
    [
        ("/", 1, "posts", "create", 1, 1),
        (f"/profile/{user_username[1]}", 1, "posts", "create", 1, 1),
        ("/user/messages", 2, "user", "send_message", 1, 2),
    ],
    ids=["index", "profile", "messages"],
)
def test_pagination_nav(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    routes: Routes,
    test_object: int,
    authorize_user: AuthorizeUserFixtureType,
    route: str,
    prop: str,
    method: str,
    user_do: int,
    user_view: int,
) -> None:
    """Test links are rendered when more than one page exists.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param client: Test application client.
    :param routes: Work with application routes.
    :param test_object: Base object for test objects.
    :param authorize_user: Authorize existing user.
    :param route: Route to test pagination with.
    :param prop: Property belonging to ``routes``.
    :param method: Method to test pagination with.
    :param user_do: User index to perform task with.
    :param user_view: User index to view page result with.
    """
    # every post apart from the first one will add functionality to the
    # pagination footer navbar
    monkeypatch.setenv("POSTS_PER_PAGE", "1")
    config.init_app(test_app)
    routes.auth.register_index(1, confirm=True)
    routes.auth.register_index(2, confirm=True)
    authorize_user(1)
    routes.auth.login_index(user_do)

    # add two posts to add an extra page
    getattr(getattr(routes, prop), method)(test_object)
    getattr(getattr(routes, prop), method)(test_object)

    routes.auth.logout()

    routes.auth.login_index(user_view)
    response = client.get(route)
    assert b'<li class="page-item disabled">' in response.data
    assert b'<a class="page-link" href="#" tabindex="-1">' in response.data
    assert b"Previous" in response.data
    assert b'<li class="page-item">' in response.data
    assert b"?page=2" in response.data
    assert b"Next" in response.data

    response = client.get(f"{route}?page=2")
    assert b'<li class="page-item disabled">' in response.data
    assert b'<a class="page-link" href="#" tabindex="-1">' in response.data
    assert b"Previous" in response.data
    assert b'<li class="page-item">' in response.data
    assert b"?page=1" in response.data
    assert b"Next" in response.data


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize(
    "key,value",
    [
        ("Strict-Transport-Security", ["max-age=31556926; includeSubDomains"]),
        ("X-Frame-Options", ["SAMEORIGIN"]),
        ("X-XSS-Protection", ["1; mode=block"]),
        ("X-Content-Type-Options", ["nosniff"]),
        ("Referrer-Policy", ["strict-origin-when-cross-origin"]),
        ("Cache-Control", []),
    ],
    ids=[
        "Strict-Transport-Security",
        "X-Frame-Options",
        "X-XSS-Protection",
        "X-Content-Type-Options",
        "Referrer-Policy",
        "Cache-Control",
    ],
)
def test_headers(client: FlaskClient, key: str, value: str) -> None:
    """Assert headers are secure.

    :param client: Test application client.
    :param key: Header key.
    :param value: Header's value.
    """
    response = client.get("/")
    assert response.headers.getlist(key) == value


def test_csp_report(
    monkeypatch: pytest.MonkeyPatch, test_app: Flask, client: FlaskClient
) -> None:
    """Test response for CSP violations route.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param client: Test application client.
    """
    with test_app.app_context():
        captured = Recorder()
        monkeypatch.setattr(
            "app.routes.report.current_app.logger.info", captured
        )
        application_csp_report = b'{"csp-report":{"report_stuff":"here"}}'
        response = client.post(
            "/report/csp_violations", data=application_csp_report
        )
        assert response.status_code == 204
        expected = (
            '{\n    "csp-report": {\n        "report_stuff": "here"\n    }\n}'
        )
        assert expected in captured.args


@pytest.mark.parametrize(
    "default,add,expected",
    [
        ({}, {}, {}),
        ({"k": "1"}, {}, {"k": "1"}),
        ({}, {"k": "2"}, {"k": "2"}),
        ({"k": "1"}, {"k": ["1"]}, {"k": "1"}),
        ({"k": "1"}, {"k": "2"}, {"k": ["1", "2"]}),
        ({"k": "1"}, {"k": ["2"]}, {"k": ["1", "2"]}),
        ({"k": ["1", "2"]}, {"k": ["3"]}, {"k": ["1", "2", "3"]}),
        ({"k": ["1", "2"]}, {"k": ["3", "4"]}, {"k": ["1", "2", "3", "4"]}),
    ],
    ids=[
        "no-fields",
        "no-add",
        "only-add",
        "add-diff-type-no-change",
        "merge",
        "merge-one-to-one",
        "merge-one-to-two",
        "merge-two-to-two",
    ],
)
def test_csp_class(default: CSPType, add: CSPType, expected: CSPType) -> None:
    """Test the ``ContentSecurityPolicy`` object.

    Test the assigning of a default policy, and the addition of any
    custom configured policy items.

    :param default: The policy to start with.
    :param add: The configured policy directive to add to the existing
        policy.
    :param expected: The expected
    """
    csp = ContentSecurityPolicy(default)
    csp.update_policy(add)
    assert dict(csp) == expected


def test_jinja2_required_extensions() -> None:
    """Test ``jinja2.ext`` has attrs needed for language support."""
    # noinspection PyUnresolvedReferences
    assert hasattr(jinja2_ext, "autoescape")
    assert hasattr(jinja2_ext, "with_")


# noinspection DuplicatedCode
def test_translate_init_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    runner: FlaskCliRunner,
) -> None:
    """Test management of files when running ``flask translate init``.

    :param tmp_path: Create and return temporary ``Path`` object.
    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param runner: Test application cli.
    """
    pot_file = tmp_path / MESSAGES_POT
    tdir: Path = test_app.config["TRANSLATIONS_DIR"]
    lang_arg = "es"
    lc_dir = tdir / lang_arg / "LC_MESSAGES"
    po_file = lc_dir / MESSAGES_PO

    def _extract():
        pot_file.write_text(POT_CONTENTS)

    def _init():
        lc_dir.mkdir(parents=True)
        shutil.copy2(pot_file, po_file)

    commands = [_extract, _init]

    def _pybabel(_: str, *__: str | os.PathLike) -> None:
        commands.pop(0)()

    monkeypatch.setattr(APP_UTILS_LANG_POT_FILE, lambda: pot_file)
    monkeypatch.setattr("app.utils.lang._pybabel", _pybabel)
    result = runner.invoke(
        args=["translate", "init", lang_arg], catch_exceptions=False
    )
    po_contents = po_file.read_text(encoding="utf-8")
    assert "<Result okay>" in str(result)
    assert POT_CONTENTS[-3:] == '"\n\n'
    assert not pot_file.is_file()
    assert po_contents[-3:] == '""\n'
    assert f"{COPYRIGHT_AUTHOR} <{COPYRIGHT_EMAIL}>, 2022" in po_contents
    assert f"Report-Msgid-Bugs-To: {COPYRIGHT_EMAIL}" in po_contents
    assert (
        f"Last-Translator: {COPYRIGHT_AUTHOR} <{COPYRIGHT_EMAIL}>"
        in po_contents
    )
    assert "FIRST AUTHOR" not in po_contents
    assert "EMAIL@ADDRESS" not in po_contents


# noinspection DuplicatedCode
def test_translate_update_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    runner: FlaskCliRunner,
) -> None:
    """Test management of files when running ``flask translate update``.

    :param tmp_path: Create and return temporary ``Path`` object.
    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param runner: Test application cli.
    """
    pot_file = tmp_path / MESSAGES_POT
    tdir: Path = test_app.config["TRANSLATIONS_DIR"]
    lang_arg = "es"
    lc_dir = tdir / lang_arg / "LC_MESSAGES"
    po_file = lc_dir / MESSAGES_PO

    def _extract():
        pot_file.write_text(POT_CONTENTS)

    def _init():
        lc_dir.mkdir(parents=True)
        shutil.copy2(pot_file, po_file)

    def _update():
        shutil.copy2(pot_file, po_file)

    _extract()
    _init()
    os.remove(pot_file)

    commands = [_extract, _update]

    def _pybabel(_: str, *__: str | os.PathLike) -> None:
        commands.pop(0)()

    monkeypatch.setattr(APP_UTILS_LANG_POT_FILE, lambda: pot_file)
    monkeypatch.setattr("app.utils.lang._pybabel", _pybabel)
    result = runner.invoke(
        args=["translate", "update"], catch_exceptions=False
    )
    po_contents = po_file.read_text(encoding="utf-8")
    assert "<Result okay>" in str(result)
    assert POT_CONTENTS[-3:] == '"\n\n'
    assert not pot_file.is_file()
    assert po_contents[-3:] == '""\n'
    assert f"{COPYRIGHT_AUTHOR} <{COPYRIGHT_EMAIL}>, 2022" in po_contents
    assert f"Report-Msgid-Bugs-To: {COPYRIGHT_EMAIL}" in po_contents
    assert (
        f"Last-Translator: {COPYRIGHT_AUTHOR} <{COPYRIGHT_EMAIL}>"
        in po_contents
    )
    assert "FIRST AUTHOR" not in po_contents
    assert "EMAIL@ADDRESS" not in po_contents


# noinspection DuplicatedCode
def test_translate_args(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: FlaskCliRunner
) -> None:
    """Test commands called when invoking ``flask translate init``.

    :param tmp_path: Create and return temporary ``Path`` object.
    :param monkeypatch: Mock patch environment and attributes.
    :param runner: Test application cli.
    """
    commands = []
    pot_file = tmp_path / MESSAGES_POT
    monkeypatch.setattr(APP_UTILS_LANG_POT_FILE, lambda: pot_file)

    def _subprocess_run(args: t.List[str | os.PathLike], **_: bool) -> None:
        commands.extend(args)
        pot_file.write_text(POT_CONTENTS)

    monkeypatch.setattr(APP_UTILS_LANG_SUBPROCESS_RUN, _subprocess_run)
    runner.invoke(args=["translate", "init", "es"])
    assert "pybabel" in commands
    assert "extract" in commands
    assert "init" in commands


# noinspection DuplicatedCode
def test_translate_update_args(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: FlaskCliRunner
) -> None:
    """Test commands called when invoking ``flask translate update``.

    :param tmp_path: Create and return temporary ``Path`` object.
    :param monkeypatch: Mock patch environment and attributes.
    :param runner: Test application cli.
    """
    commands = []
    pot_file = tmp_path / MESSAGES_POT
    monkeypatch.setattr(APP_UTILS_LANG_POT_FILE, lambda: pot_file)

    def _subprocess_run(args: t.List[str | os.PathLike], **_: bool) -> None:
        commands.extend(args)
        pot_file.write_text(POT_CONTENTS)

    monkeypatch.setattr(APP_UTILS_LANG_SUBPROCESS_RUN, _subprocess_run)
    runner.invoke(args=["translate", "update"])
    assert "pybabel" in commands
    assert "extract" in commands


# noinspection DuplicatedCode
def test_translate_compile(
    monkeypatch: pytest.MonkeyPatch, test_app: Flask, runner: FlaskCliRunner
) -> None:
    """Test commands called when invoking ``flask translate compile``.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param runner: Test application cli.
    """
    po_file: Path = (
        test_app.config["TRANSLATIONS_DIR"]
        / "es"
        / "LC_MESSAGES"
        / MESSAGES_PO
    )
    commands = []
    monkeypatch.setattr(
        APP_UTILS_LANG_SUBPROCESS_RUN, lambda x, **y: commands.extend(x)
    )
    result = runner.invoke(
        args=["translate", "compile"], catch_exceptions=False
    )
    assert "No message catalogs to compile" in result.output
    assert not commands
    po_file.parent.mkdir(parents=True)
    po_file.touch()
    runner.invoke(args=["translate", "compile"], catch_exceptions=False)
    assert "pybabel" in commands
    assert "compile" in commands


def test_pot_file(test_app: Flask) -> None:
    """Test ``_pot_file`` which is monkeypatched above.

    :param test_app: Test application.
    """
    with test_app.app_context():
        assert lang._pot_file() == Path(MESSAGES_POT)
