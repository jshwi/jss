"""
tests._test
===========
"""
# pylint: disable=too-many-arguments,too-many-lines,too-many-locals
# pylint: disable=import-outside-toplevel,protected-access
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
from dominate import tags
from dominate.tags import html_tag
from flask import Flask, session
from flask.testing import FlaskClient, FlaskCliRunner
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer
from markupsafe import Markup
from redis import RedisError

from app import config
from app.extensions import mail
from app.log import smtp_handler
from app.models import Post, User, db
from app.utils import lang
from app.utils.csp import ContentSecurityPolicy, CSPType
from app.utils.mail import send_email
from app.utils.register import RegisterContext

from .utils import (
    ADMIN_ROUTE,
    ADMIN_USER_EMAIL,
    ADMIN_USER_PASSWORD,
    ADMIN_USER_ROUTE,
    ADMIN_USER_USERNAME,
    APP_MODELS_JOB_FETCH,
    APP_UTILS_LANG_POT_FILE,
    APP_UTILS_LANG_SUBPROCESS_RUN,
    AUTHORIZED_USER_EMAIL,
    AUTHORIZED_USER_PASSWORD,
    AUTHORIZED_USER_USERNAME,
    COPYRIGHT_AUTHOR,
    COPYRIGHT_EMAIL,
    COPYRIGHT_YEAR,
    COVERED_ROUTES,
    INVALID_OR_EXPIRED,
    LAST_USER_EMAIL,
    LAST_USER_PASSWORD,
    LAST_USER_USERNAME,
    LICENSE,
    MAIL_PASSWORD,
    MAIL_PORT,
    MAIL_SERVER,
    MAIL_USERNAME,
    MAIN_USER_EMAIL,
    MAIN_USER_PASSWORD,
    MAIN_USER_USERNAME,
    MESSAGE_BODY,
    MESSAGE_CREATED,
    MESSAGES_PO,
    MESSAGES_POT,
    MISC_PROGRESS_INT,
    OTHER_USER_EMAIL,
    OTHER_USER_PASSWORD,
    OTHER_USER_USERNAME,
    POST_1,
    POST_AUTHOR_ID_1,
    POST_AUTHOR_ID_2,
    POST_AUTHOR_ID_3,
    POST_AUTHOR_ID_4,
    POST_BODY_1,
    POST_BODY_2,
    POST_BODY_3,
    POST_BODY_4,
    POST_BODY_V1,
    POST_BODY_V2,
    POST_BODY_V3,
    POST_CREATED_1,
    POST_CREATED_2,
    POST_CREATED_3,
    POST_CREATED_4,
    POST_TITLE_1,
    POST_TITLE_2,
    POST_TITLE_3,
    POST_TITLE_4,
    POST_TITLE_V1,
    POST_TITLE_V2,
    POST_TITLE_V3,
    POT_CONTENTS,
    PROFILE_EDIT,
    PYPROJECT_TOML,
    RECIPIENT_ID,
    REDIRECT_LOGOUT,
    SENDER_ID,
    STATUS_CODE_TO_ROUTE_DEFAULT,
    TASK_DESCRIPTION,
    TASK_ID,
    TASK_NAME,
    UPDATE1,
    AddTestObjects,
    AuthActions,
    MessageTestObject,
    PostTestObject,
    Recorder,
    TaskTestObject,
    TestObject,
    UserTestObject,
)


@pytest.mark.usefixtures("init_db")
def test_register(
    test_app: Flask, client: FlaskClient, auth: AuthActions
) -> None:
    """The register view should render successfully on ``GET``.

    On ``POST``, with valid form data, it should redirect to the login
    URL and the user's data should be in the database. Invalid data
    should display error messages.

    To test that the page renders successfully a simple request is made
    and checked for a ``200 OK`` ``status_code``.

    Headers will have a ``Location`` object with the login URL when the
    register view redirects to the login view.

    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    """
    assert client.get("/auth/register").status_code == 200
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    response = auth.register(user_test_object)
    assert response.headers["Location"] == "https://localhost/auth/unconfirmed"
    with test_app.app_context():
        user = User.query.filter_by(username=user_test_object.username).first()
        assert user is not None


@pytest.mark.usefixtures("init_db")
def test_login(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test login functionality.

    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    response = auth.login(user_test_object)
    assert response.headers["Location"] == "https://localhost/auth/unconfirmed"
    with client:
        client.get("/")
        assert current_user.username == user_test_object.username


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize(
    "username,password",
    [
        ("not-a-username", MAIN_USER_PASSWORD),
        (MAIN_USER_USERNAME, "not-a-password"),
    ],
    ids=["incorrect-username", "incorrect-password"],
)
def test_login_validate(
    auth: AuthActions,
    add_test_objects: AddTestObjects,
    username: str,
    password: str,
) -> None:
    """Test incorrect username and password error messages.

    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    :param username: Parametrized incorrect username
    :param password: Parametrized incorrect password
    """
    registered_user = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(registered_user)
    test_user = UserTestObject(username, OTHER_USER_EMAIL, password)
    response = auth.login(test_user)
    assert b"Invalid username or password" in response.data


@pytest.mark.usefixtures("init_db")
def test_logout(client: FlaskClient, auth: AuthActions) -> None:
    """Test logout functionality.

    :param client: Client for testing app.
    :param auth: Handle authorization with test app.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    auth.login(user_test_object)
    with client:
        client.get(REDIRECT_LOGOUT)
        assert "user_id" not in session


@pytest.mark.usefixtures("init_db")
def test_index(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test login and subsequent requests from the client.

    The index view should display information about the post that was
    added with the test data. When logged in as the author there should
    be a link to edit the post.

    We can also test some more authentication behaviour while testing
    the index view. When not logged in each page shows links to log in
    or register. When logged in there's a link to log out.

    :param client: Client for testing app.
    :param auth: Handle authorization with test app.
    """
    response = client.get("/")
    assert b"Login" in response.data
    assert b"Register" in response.data
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME,
        MAIN_USER_EMAIL,
        MAIN_USER_PASSWORD,
        confirmed=True,
        authorized=True,
    )
    post_test_object = PostTestObject(
        POST_TITLE_1, POST_BODY_1, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    add_test_objects.add_test_users(user_test_object)
    add_test_objects.add_test_posts(post_test_object)
    auth.login(user_test_object)
    decoded_response = client.get("/").data.decode()
    assert "Logout" in decoded_response
    assert post_test_object.title in decoded_response
    assert user_test_object.username in decoded_response
    assert post_test_object.body in decoded_response
    assert 'href="/post/1/update"' in decoded_response


@pytest.mark.parametrize(
    "route", ["/post/create", UPDATE1, "/redirect/1/delete"]
)
def test_login_required(client: FlaskClient, route: str) -> None:
    """Test requirement that user be logged in to post.

    A user must be logged in to access the "create", "update", and
    "delete" views.

    The logged-in user must be the author of the post to access the
    update and delete views, otherwise a ``403 Forbidden`` status is
    returned.

    :param client: Client for testing app.
    :param route: Parametrized route path.
    """
    response = client.post(route, follow_redirects=True)
    assert response.status_code == 401


@pytest.mark.usefixtures("init_db")
def test_author_required(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test author's name when required.

    The create and update views should render and return a ``200 OK``
    status for a ``GET`` request.

    When valid data is sent in a ``POST`` request the create view should
    insert the new post data into the database and the update view
    should modify the existing data. Both pages should show an error
    message on invalid data.

    :param test_app: Test ``Flask`` app object.
    :param client: Client for testing app.
    :param auth: Handle authorization with test app.
    """
    user_test_object = UserTestObject(
        AUTHORIZED_USER_USERNAME,
        AUTHORIZED_USER_EMAIL,
        AUTHORIZED_USER_PASSWORD,
        authorized=True,
    )
    other_user_test_object = UserTestObject(
        OTHER_USER_USERNAME, OTHER_USER_EMAIL, OTHER_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object, other_user_test_object)
    post_test_object = PostTestObject(
        POST_TITLE_1, POST_BODY_1, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    add_test_objects.add_test_posts(post_test_object)
    # change the post author to another author
    with test_app.app_context():
        post = Post.query.get(1)
        post.user_id = 2
        db.session.commit()

    auth.login(user_test_object)
    # current user cannot modify other user's post
    assert client.post(UPDATE1, follow_redirects=True).status_code == 403
    assert client.post("/redirect/1/delete").status_code == 403

    # current user doesn't see edit link
    assert b'href="/post/1/update"' not in client.get("/").data


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize("route", ["/2/update", "/2/delete"])
def test_exists_required(
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
    route: str,
) -> None:
    """Test ``404 Not Found`` is returned when a route does not exist.

    :param client: Client for testing app.
    :param auth: Handle authorization with test app.
    :param route: Parametrized route path.
    """
    user_test_object = UserTestObject(
        AUTHORIZED_USER_USERNAME,
        AUTHORIZED_USER_EMAIL,
        AUTHORIZED_USER_PASSWORD,
        authorized=True,
    )
    post_test_object = PostTestObject(
        POST_TITLE_1, POST_BODY_1, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    add_test_objects.add_test_users(user_test_object)
    add_test_objects.add_test_posts(post_test_object)
    auth.login(user_test_object)
    response = client.post(route, follow_redirects=True)
    assert response.status_code == 404


@pytest.mark.usefixtures("init_db")
def test_create(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test create view functionality.

    When valid data is sent in a ``POST`` request the create view should
    insert the new post data into the database.

    :param test_app: Test ``Flask`` app object.
    :param client: Client for testing app.
    :param auth: Handle authorization with test app.
    """
    user_test_object = UserTestObject(
        AUTHORIZED_USER_USERNAME,
        AUTHORIZED_USER_EMAIL,
        AUTHORIZED_USER_PASSWORD,
        authorized=True,
    )
    add_test_objects.add_test_users(user_test_object)
    auth.login(user_test_object)
    assert client.get("/post/create").status_code == 200
    client.post(
        "/post/create", data={"title": POST_TITLE_1, "body": POST_BODY_1}
    )
    with test_app.app_context():
        count = Post.query.count()
        assert count == 1


@pytest.mark.usefixtures("init_db")
def test_update(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test update view modifies the existing data.

    :param test_app: Test ``Flask`` app object.
    :param client: Client for testing app.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        AUTHORIZED_USER_USERNAME,
        AUTHORIZED_USER_EMAIL,
        AUTHORIZED_USER_PASSWORD,
        authorized=True,
    )
    created_post = PostTestObject(
        POST_TITLE_1, POST_BODY_1, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    updated_post = PostTestObject(
        "updated title", "updated body", POST_AUTHOR_ID_1, POST_CREATED_1
    )
    add_test_objects.add_test_users(user_test_object)
    add_test_objects.add_test_posts(created_post)
    auth.login(user_test_object)
    assert client.get(UPDATE1, follow_redirects=True).status_code == 200
    assert "Edited" not in client.get(POST_1).data.decode()
    client.post(
        UPDATE1, data={"title": updated_post.title, "body": updated_post.body}
    )
    with test_app.app_context():
        post = Post.query.get(1)
        assert post.title == updated_post.title
        assert post.body == updated_post.body

    assert "Edited" in client.get(POST_1).data.decode()


@pytest.mark.usefixtures("init_db")
def test_delete(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test deletion of posts.

    The "delete" view should redirect to the index URl and the post
    should no longer exist in the database.

    :param test_app: Test ``Flask`` app object.
    :param client: Client for testing app.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        AUTHORIZED_USER_USERNAME,
        AUTHORIZED_USER_EMAIL,
        AUTHORIZED_USER_PASSWORD,
        authorized=True,
    )
    add_test_objects.add_test_users(user_test_object)
    post_test_object = PostTestObject(
        POST_TITLE_1, POST_BODY_1, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    add_test_objects.add_test_posts(post_test_object)
    auth.login(user_test_object)
    response = client.post("/redirect/1/delete")
    assert response.headers["Location"] == "https://localhost/"
    with test_app.app_context():
        post = Post.query.get(1)
        assert post is None


def test_create_command(
    runner: FlaskCliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test cli.

    :param runner: Fixture derived from the ``create_app`` factory
        fixture used to call the ``init-db`` command by name.
    :param monkeypatch: Mock patch environment and attributes.
    """
    # flask create user
    state_1 = Recorder()
    monkeypatch.setattr("app.cli.create_user_cli", state_1)
    runner.invoke(args=["create", "user"])
    assert state_1.called

    # flask create admin
    state_2 = Recorder()
    monkeypatch.setattr("app.cli.create_admin_cli", state_2)
    runner.invoke(args=["create", "admin"])
    assert state_2.called


def test_export() -> None:
    """Test export (to dict_ function for models."""
    # noinspection PyArgumentList
    post = Post(title=POST_TITLE_1, body=POST_BODY_1, created=POST_CREATED_1)
    as_dict = post.export()
    assert as_dict["title"] == POST_TITLE_1
    assert as_dict["body"] == POST_BODY_1
    assert as_dict["created"] == str(POST_CREATED_1)


@pytest.mark.parametrize("sync", [True, False])
def test_send_mail(test_app: Flask, sync: bool) -> None:
    """Test sending of mail by app's email client.

    :param test_app: Test ``Flask`` app object.
    :param sync: Asynchronous: True or False.
    """
    subject = "mail subject line"
    recipients = [MAIN_USER_EMAIL, OTHER_USER_EMAIL]
    html = "<p>email body<p>"
    sender = "admin@localhost"
    data = {
        "title": POST_TITLE_1,
        "body": POST_BODY_1,
        "created": f"{POST_CREATED_1.isoformat()}Z",
    }
    attachment = {
        "filename": "file.json",
        "content_type": "application/json",
        "data": json.dumps({"posts": data}, indent=4),
    }
    with mail.record_messages() as outbox:
        with test_app.app_context():
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


@pytest.mark.usefixtures("init_db")
def test_create_user_no_exist(
    test_app: Flask,
    runner: FlaskCliRunner,
    patch_getpass: t.Callable[[t.List[str]], None],
) -> None:
    """Test creation of a new user that doesn't exist.

    :param test_app: Test ``Flask`` app object.
    :param runner: Fixture derived from the ``create_app`` factory
        fixture used to call the ``init-db`` command by name.
    """
    user_input = f"{MAIN_USER_USERNAME}\n{MAIN_USER_EMAIL}\n"
    patch_getpass([MAIN_USER_PASSWORD, MAIN_USER_PASSWORD])
    response = runner.invoke(args=["create", "user"], input=user_input)
    assert "user successfully created" in response.output
    with test_app.app_context():
        user = User.query.filter_by(username=MAIN_USER_USERNAME).first()
        assert user.email == MAIN_USER_EMAIL
        assert user.check_password(MAIN_USER_PASSWORD)


@pytest.mark.parametrize(
    "username,email,expected",
    [
        (MAIN_USER_USERNAME, "unique@test.com", "username is taken"),
        (
            "unique",
            MAIN_USER_EMAIL,
            "a user with this email address is already registered",
        ),
    ],
    ids=["username", "email"],
)
@pytest.mark.usefixtures("init_db")
def test_create_user_exists(
    runner: FlaskCliRunner,
    add_test_objects: AddTestObjects,
    username: str,
    email: str,
    expected: str,
) -> None:
    """Test creation of a new user that exists.

    :param runner: Fixture derived from the ``create_app`` factory
        fixture used to call the ``init-db`` command by name.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    response = runner.invoke(
        args=["create", "user"], input=f"{username}\n{email}\n"
    )
    assert expected in response.output


@pytest.mark.usefixtures("init_db")
def test_create_user_email_exists(
    runner: FlaskCliRunner, add_test_objects: AddTestObjects
) -> None:
    """Test creation of a new user whose email is already registered.

    :param runner: Fixture derived from the ``create_app`` factory
        fixture used to call the ``init-db`` command by name.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    user_input = f"{OTHER_USER_EMAIL}\n{MAIN_USER_EMAIL}"
    add_test_objects.add_test_users(user_test_object)
    response = runner.invoke(args=["create", "user"], input=user_input)
    assert (
        "a user with this email address is already registered"
        in response.output
    )


@pytest.mark.usefixtures("init_db")
def test_create_user_passwords_no_match(
    runner: FlaskCliRunner, patch_getpass: t.Callable[[t.List[str]], None]
) -> None:
    """Test creation of a new user where passwords don't match.

    :param runner: Fixture derived from the ``create_app`` factory
        fixture used to call the ``init-db`` command by name.
    """
    user_input = f"{MAIN_USER_USERNAME}\n{MAIN_USER_EMAIL}\n"
    patch_getpass([MAIN_USER_PASSWORD, OTHER_USER_PASSWORD])
    response = runner.invoke(args=["create", "user"], input=user_input)
    assert "passwords do not match: could not add user" in response.output


@pytest.mark.usefixtures("init_db")
def test_create_admin(test_app: Flask, runner: FlaskCliRunner) -> None:
    """Test commands called when invoking ``flask create admin``.

    :param test_app: Test ``Flask`` app object.
    :param runner: Fixture derived from the ``create_app`` factory
        fixture used to call the ``init-db`` command by name.
    """
    response = runner.invoke(args=["create", "admin"])
    assert "admin successfully created" in response.output
    with test_app.app_context():
        admin = User.query.filter_by(username="admin").first()
        assert admin.email == test_app.config["ADMINS"][0]
        assert admin.check_password(ADMIN_USER_PASSWORD)


def test_404_error(client: FlaskClient) -> None:
    """Test ``404 Not Found`` is returned when a route does not exist.

    :param client: Client for testing app.
    """
    response = client.post("/does_not_exist")
    assert response.status_code == 404


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize(
    "route", ["/post/create", UPDATE1, "/redirect/1/delete"]
)
def test_admin_required(
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
    route: str,
) -> None:
    """Test requirement that admin user be logged in to post.

    An admin user must be logged in to access the "create", "update",
    and "delete" views.

    The logged-in user must be the author of the post to access the
    update and delete views, otherwise a ``403 Forbidden`` status is
    returned.

    :param client: Client for testing app.
    :param auth: Handle authorization with test app.
    :param route: Parametrized route path.
    """
    user_test_object = UserTestObject(
        ADMIN_USER_USERNAME, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD, admin=False
    )
    add_test_objects.add_test_users(user_test_object)
    auth.login(user_test_object)
    response = client.post(route, follow_redirects=True)
    assert response.status_code == 401


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize(
    "username,email,message",
    [
        (MAIN_USER_USERNAME, OTHER_USER_EMAIL, b"Username is taken"),
        (OTHER_USER_USERNAME, MAIN_USER_EMAIL, b"already registered"),
    ],
    ids=["username", "email"],
)
def test_register_invalid_fields(
    auth: AuthActions,
    add_test_objects: AddTestObjects,
    username: str,
    email: str,
    message: str,
) -> None:
    """Test different invalid input and error messages.

    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    :param username: The test username input.
    :param message: The expected message for the response.
    """
    user_test_object = UserTestObject(
        username=MAIN_USER_USERNAME,
        email=MAIN_USER_EMAIL,
        password=MAIN_USER_PASSWORD,
    )
    add_test_objects.add_test_users(user_test_object)
    new_user_test_object = UserTestObject(username, email, MAIN_USER_PASSWORD)
    response = auth.register(new_user_test_object)
    assert message in response.data


@pytest.mark.usefixtures("init_db")
def test_confirmation_email_unconfirmed(
    test_app: Flask, client: FlaskClient, auth: AuthActions
) -> None:
    """Test user is moved from confirmed as False to True.

    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    with mail.record_messages() as outbox:
        auth.register(user_test_object)
        response = client.get("auth/unconfirmed")
        assert b"A confirmation email has been sent." in response.data
        with test_app.app_context():
            user = User.query.filter_by(
                username=user_test_object.username
            ).first()
            assert user.confirmed is False
            auth.follow_token_route(outbox[0].html, follow_redirects=True)
            assert user.confirmed is True


@pytest.mark.usefixtures("init_db")
def test_confirmation_email_confirmed(
    test_app: Flask, auth: AuthActions
) -> None:
    """Test user redirected when already confirmed.

    :param test_app: Test ``Flask`` app object.
    :param auth: Handle authorization with test app.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    with mail.record_messages() as outbox:
        auth.register(user_test_object)
        with test_app.app_context():
            user = User.query.filter_by(
                username=user_test_object.username
            ).first()
            user.confirmed = True
            db.session.commit()
            response = auth.follow_token_route(
                outbox[0].html, follow_redirects=True
            )
            assert b"Account already confirmed. Please login." in response.data


@pytest.mark.usefixtures("init_db")
def test_confirmation_email_expired(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
) -> None:
    """Test user denied when confirmation is expired. Allow resend.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    with mail.record_messages() as outbox:
        auth.register(user_test_object)
        with test_app.app_context():
            route = auth.parse_token_route(outbox[0].html)
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
            assert INVALID_OR_EXPIRED in response.data.decode()


@pytest.mark.usefixtures("init_db")
def test_login_confirmed(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test login functionality once user is verified.

    :param test_app: Test ``Flask`` app object.
    :param client: Flask client testing helper.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    with test_app.app_context():
        user = User.query.filter_by(username=user_test_object.username).first()
        user.confirmed = True
        db.session.commit()

    response = auth.login(user_test_object)
    assert response.headers["Location"] == "https://localhost/"
    with client:
        client.get("/")
        assert current_user.username == user_test_object.username


@pytest.mark.usefixtures("init_db")
def test_confirmation_email_resend(
    client: FlaskClient, auth: AuthActions
) -> None:
    """Test user receives email when requesting resend.

    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    auth.register(user_test_object)
    response = client.get("/redirect/resend", follow_redirects=True)
    assert b"A new confirmation email has been sent." in response.data


@pytest.mark.usefixtures("init_db")
def test_request_password_reset_email(
    auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test that the correct email is sent to user for password reset.

    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    with mail.record_messages() as outbox:
        auth.request_password_reset(MAIN_USER_EMAIL, follow_redirects=True)

    response = auth.follow_token_route(outbox[0].html, follow_redirects=True)
    assert b"Reset Password" in response.data
    assert b"Please enter your new password" in response.data


@pytest.mark.usefixtures("init_db")
def test_bad_token(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test user denied when jwt for resetting password is expired.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test ``Flask`` app object.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    with test_app.app_context():
        with mail.record_messages() as outbox:
            monkeypatch.setattr(
                "app.routes.auth.generate_reset_password_token",
                lambda *_, **__: "bad_token",
            )
            auth.request_password_reset(MAIN_USER_EMAIL, follow_redirects=True)

        response = auth.follow_token_route(
            outbox[0].html, follow_redirects=True
        )
        assert INVALID_OR_EXPIRED in response.data.decode()


@pytest.mark.usefixtures("init_db")
def test_email_does_not_exist(auth: AuthActions) -> None:
    """Test user notified when email does not exist for password reset.

    :param auth: Handle authorization with test app.
    """
    response = auth.request_password_reset(MAIN_USER_EMAIL)
    assert b"An account with that email address doesn't exist" in response.data


@pytest.mark.usefixtures("init_db")
def test_redundant_token(
    test_app: Flask, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test user notified that them being logged in has voided token.

    :param test_app: Test ``Flask`` app object.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    with test_app.app_context():
        with mail.record_messages() as outbox:
            auth.request_password_reset(MAIN_USER_EMAIL, follow_redirects=True)

        auth.login(user_test_object)
        response = auth.follow_token_route(
            outbox[0].html, follow_redirects=True
        )
        assert INVALID_OR_EXPIRED in response.data.decode()


@pytest.mark.usefixtures("init_db")
def test_reset_password(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test the password reset process.

    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    with mail.record_messages() as outbox:
        auth.request_password_reset(MAIN_USER_EMAIL, follow_redirects=True)

    with test_app.app_context():
        user = User.query.filter_by(username=user_test_object.username).first()
        assert user.check_password(MAIN_USER_PASSWORD)
        client.post(
            auth.parse_token_route(outbox[0].html),
            data={
                "password": OTHER_USER_PASSWORD,
                "confirm_password": OTHER_USER_PASSWORD,
            },
        )
        assert not user.check_password(MAIN_USER_PASSWORD)
        assert user.check_password(OTHER_USER_PASSWORD)


@pytest.mark.parametrize("use_tls,secure", [(False, None), (True, ())])
def test_get_smtp_handler(
    monkeypatch: pytest.MonkeyPatch, use_tls: bool, secure: t.Optional[tuple]
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
    app.logger.addHandler = (  # type: ignore
        # pylint: disable=unnecessary-lambda
        lambda x: app.logger.handlers.append(x)  # type: ignore
    )
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


def test_avatar() -> None:
    """Test generated avatar URL for expected value."""
    # noinspection PyArgumentList
    user = User(username=ADMIN_USER_USERNAME, email=ADMIN_USER_EMAIL)
    assert user.avatar(128) == (
        "https://gravatar.com/avatar/"
        "5b37040e6200edb3c7f409e994076872?d=identicon&s=128"
    )


@pytest.mark.usefixtures("init_db")
def test_profile_page(
    client: FlaskClient, add_test_objects: AddTestObjects
) -> None:
    """Test response when visiting profile page of existing user.

    :param client: App's test-client API.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    response = client.get(f"/profile/{MAIN_USER_USERNAME}")
    assert b'src="https://gravatar.com/avatar/' in response.data


@pytest.mark.usefixtures("init_db")
def test_post_page(
    client: FlaskClient, add_test_objects: AddTestObjects
) -> None:
    """Test for correct contents in post page response.

    :param client: App's test-client API.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    post_test_object = PostTestObject(
        POST_TITLE_1, POST_BODY_1, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    add_test_objects.add_test_users(user_test_object)
    add_test_objects.add_test_posts(post_test_object)
    response = client.get(POST_1)
    assert (
        f"    <h1>\n     {POST_TITLE_1}\n    </h1>\n"
    ) in response.data.decode()
    assert POST_BODY_1 in response.data.decode()


@pytest.mark.usefixtures("init_db")
def test_edit_profile(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test edit profile page.

    :param client: App's test-client API.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD, confirmed=True
    )
    add_test_objects.add_test_users(user_test_object)
    auth.login(user_test_object)
    response = client.get(PROFILE_EDIT, follow_redirects=True)
    assert b"Edit Profile" in response.data
    assert b"Profile" in response.data
    assert b"Logout" in response.data
    assert b"Edit Profile" in response.data
    assert MAIN_USER_USERNAME in response.data.decode()
    assert b"About me" in response.data
    response = client.post(
        PROFILE_EDIT,
        data={"username": OTHER_USER_USERNAME, "about_me": "testing about me"},
        follow_redirects=True,
    )
    assert OTHER_USER_USERNAME in response.data.decode()
    assert b"testing about me" in response.data


@pytest.mark.usefixtures("init_db")
def test_unconfirmed(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test when unconfirmed user tries to enter restricted view.

    :param client: App's test-client API.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    auth.login(user_test_object)
    response = client.get(PROFILE_EDIT, follow_redirects=True)
    assert b"Account Verification Pending" in response.data
    assert b"You have not verified your account" in response.data
    assert b"Please check your inbox " in response.data
    assert b"or junk folder for a confirmation link." in response.data
    assert b"Didn't get the email?" in response.data
    assert b"Resend" in response.data


@pytest.mark.usefixtures("init_db")
def test_follow(test_app: Flask, add_test_objects: AddTestObjects) -> None:
    """Test functionality of user follows.

    :param test_app: Test ``Flask`` app object.
    :param add_test_objects: Add test objects to test database.
    """
    with test_app.app_context():
        user_test_object_1 = UserTestObject(
            ADMIN_USER_USERNAME, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD
        )
        user_test_object_2 = UserTestObject(
            MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
        )
        add_test_objects.add_test_users(user_test_object_1, user_test_object_2)
        user_1 = User.query.filter_by(username=ADMIN_USER_USERNAME).first()
        user_2 = User.query.filter_by(username=MAIN_USER_USERNAME).first()
        assert user_1.followed.all() == []
        assert user_1.followers.all() == []
        user_1.follow(user_2)
        db.session.commit()
        assert user_1.is_following(user_2)
        assert user_1.followed.count() == 1
        assert user_1.followed.first().username == MAIN_USER_USERNAME
        assert user_2.followers.count() == 1
        assert user_2.followers.first().username == ADMIN_USER_USERNAME
        user_1.unfollow(user_2)
        db.session.commit()
        assert not user_1.is_following(user_2)
        assert user_1.followed.count() == 0
        assert user_2.followers.count() == 0


@pytest.mark.usefixtures("init_db")
def test_follow_posts(
    test_app: Flask, add_test_objects: AddTestObjects
) -> None:
    """Test functionality of post follows.

    :param test_app: Test ``Flask`` app object.
    :param add_test_objects: Add test objects to test database.
    """
    with test_app.app_context():
        # create four users
        user_test_object_1 = UserTestObject(
            ADMIN_USER_USERNAME, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD
        )
        user_test_object_2 = UserTestObject(
            MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
        )
        user_test_object_3 = UserTestObject(
            OTHER_USER_USERNAME, OTHER_USER_EMAIL, OTHER_USER_PASSWORD
        )
        user_test_object_4 = UserTestObject(
            LAST_USER_USERNAME, LAST_USER_EMAIL, LAST_USER_PASSWORD
        )
        add_test_objects.add_test_users(
            user_test_object_1,
            user_test_object_2,
            user_test_object_3,
            user_test_object_4,
        )
        post_test_object_1 = PostTestObject(
            POST_TITLE_1, POST_BODY_1, POST_AUTHOR_ID_1, POST_CREATED_1
        )
        post_test_object_2 = PostTestObject(
            POST_TITLE_2, POST_BODY_2, POST_AUTHOR_ID_2, POST_CREATED_4
        )
        post_test_object_3 = PostTestObject(
            POST_TITLE_3, POST_BODY_3, POST_AUTHOR_ID_3, POST_CREATED_3
        )
        post_test_object_4 = PostTestObject(
            POST_TITLE_4, POST_BODY_4, POST_AUTHOR_ID_4, POST_CREATED_2
        )
        add_test_objects.add_test_posts(
            post_test_object_1,
            post_test_object_2,
            post_test_object_3,
            post_test_object_4,
        )
        user_1 = User.query.filter_by(username=ADMIN_USER_USERNAME).first()
        user_2 = User.query.filter_by(username=MAIN_USER_USERNAME).first()
        user_3 = User.query.filter_by(username=OTHER_USER_USERNAME).first()
        user_4 = User.query.filter_by(username=LAST_USER_USERNAME).first()
        post_1 = Post.query.filter_by(title=POST_TITLE_1).first()
        post_2 = Post.query.filter_by(title=POST_TITLE_2).first()
        post_3 = Post.query.filter_by(title=POST_TITLE_3).first()
        post_4 = Post.query.filter_by(title=POST_TITLE_4).first()

        # set up the followers
        user_1.follow(user_2)
        user_1.follow(user_4)
        user_2.follow(user_3)
        user_3.follow(user_4)
        db.session.commit()

        # check the followed posts of each user
        followed_1 = user_1.followed_posts().all()
        followed_2 = user_2.followed_posts().all()
        followed_3 = user_3.followed_posts().all()
        followed_4 = user_4.followed_posts().all()
        assert followed_1 == [post_2, post_4, post_1]
        assert followed_2 == [post_2, post_3]
        assert followed_3 == [post_3, post_4]
        assert followed_4 == [post_4]


@pytest.mark.usefixtures("init_db")
def test_post_follow_unfollow_routes(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test ``POST`` request to follow and unfollow a user.

    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    # create and log in test users
    user_test_object_1 = UserTestObject(
        ADMIN_USER_USERNAME,
        ADMIN_USER_EMAIL,
        ADMIN_USER_PASSWORD,
        confirmed=True,
    )
    user_test_object_2 = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD, confirmed=True
    )
    add_test_objects.add_test_users(user_test_object_1, user_test_object_2)
    auth.login(user_test_object_1)
    auth.login(user_test_object_2)
    response = client.post(
        f"/redirect/follow/{user_test_object_2.username}",
        follow_redirects=True,
    )
    assert (
        f"You are now following {user_test_object_2.username}"
        in response.data.decode()
    )
    response = client.post(
        f"/redirect/unfollow/{user_test_object_2.username}",
        follow_redirects=True,
    )
    assert (
        f"You are no longer following {MAIN_USER_USERNAME}"
        in response.data.decode()
    )


@pytest.mark.usefixtures("init_db")
def test_send_message(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test sending of personal messages from one user to another.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object_1 = UserTestObject(
        ADMIN_USER_USERNAME,
        ADMIN_USER_EMAIL,
        ADMIN_USER_PASSWORD,
        confirmed=True,
    )
    user_test_object_2 = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD, confirmed=True
    )
    add_test_objects.add_test_users(user_test_object_1, user_test_object_2)
    auth.login(user_test_object_1)
    response = client.post(
        f"/user/send_message/{user_test_object_2.username}",
        data={"message": f"test message from {user_test_object_1.username}"},
        follow_redirects=True,
    )
    assert b"Your message has been sent." in response.data
    response = client.get(f"/user/send_message/{user_test_object_2.username}")
    assert (
        f"Send Message to {user_test_object_2.username}"
        in response.data.decode()
    )
    client.get(REDIRECT_LOGOUT)
    auth.login(user_test_object_2)

    # test icon span
    monkeypatch.setenv("NAVBAR_ICONS", "1")
    config.init_app(test_app)

    # ensure the badge (<span> tag) is displayed when there are messages
    # held for the user
    response = client.get("/")
    assert all(
        i in response.data.decode()
        for i in [
            (
                '<a class="nav-link btn-lg btn-link" href="/user/messages" '
                'title="Messages">'
            ),
            '<span class="bi-bell">',
            (
                '<span class="badge badge-pill badge-primary badge-notify" '
                'id="message_count">'
            ),
            "1",
        ]
    )

    # for reliable testing ensure navbar not set to display icons
    monkeypatch.setenv("NAVBAR_ICONS", "0")
    config.init_app(test_app)

    # ensure the badge (<span> tag) is displayed when there are messages
    # held for the user
    response = client.get("/")
    assert all(
        i in response.data.decode()
        for i in [
            '<a class="nav-link" href="/user/messages" title="Messages">',
            "Messages",
            '<span class="badge" id="message_count">',
            " 1",
        ]
    )
    response = client.get("/user/notifications")
    if response.json is not None:
        obj = response.json[0]
        assert all(i in obj for i in ["data", "name", "timestamp"])
        assert all(i in obj.values() for i in [1, "unread_message_count"])

        # entering this view will confirm that the messages have been
        # viewed and there will be no badge with a count displayed
        response = client.get("/user/messages")
        assert (
            f"test message from {user_test_object_1.username}"
            in response.data.decode()
        )

    # confirm that no message badge is displayed next to the messages
    # link
    response = client.get("/")
    assert all(
        i in response.data.decode()
        for i in [
            '<a class="nav-link" href="/user/messages" title="Messages">',
            " Messages",
        ]
    )


@pytest.mark.usefixtures("init_db")
def test_export_post_is_job(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test export post function when a job already exists: is not None.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object_1 = UserTestObject(
        ADMIN_USER_USERNAME,
        ADMIN_USER_EMAIL,
        ADMIN_USER_PASSWORD,
        confirmed=True,
    )
    post_test_object = PostTestObject(
        POST_TITLE_1, POST_BODY_1, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    add_test_objects.add_test_users(user_test_object_1)
    add_test_objects.add_test_posts(post_test_object)
    auth.login(user_test_object_1)
    app_current_user = Recorder()
    app_current_user.is_authenticated = lambda: True  # type: ignore
    app_current_user.get_task_in_progress = lambda _: 1  # type: ignore
    app_current_user.username = ADMIN_USER_USERNAME  # type: ignore
    with test_app.app_context():
        app_current_user.post = Post.query.get(1)  # type: ignore
        monkeypatch.setattr(
            "app.routes.redirect.current_user", app_current_user
        )
        response = client.get("/redirect/export_posts", follow_redirects=True)

    assert b"An export task is already in progress" in response.data


@pytest.mark.usefixtures("init_db")
def test_export_post(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test export post function when a job does not exist: is None.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        ADMIN_USER_USERNAME,
        ADMIN_USER_EMAIL,
        ADMIN_USER_PASSWORD,
        confirmed=True,
    )
    post_test_object = PostTestObject(
        POST_TITLE_1, POST_BODY_1, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    add_test_objects.add_test_users(user_test_object)
    add_test_objects.add_test_posts(post_test_object)
    auth.login(user_test_object)
    enqueue = Recorder()
    session_add = Recorder()
    with test_app.app_context():
        test_app.task_queue = Recorder()  # type: ignore
        test_app.task_queue.enqueue = enqueue  # type: ignore
        test_app.task_queue.enqueue.get_id = lambda: TASK_ID  # type: ignore
        monkeypatch.setattr("app.models.User.is_authenticated", True)
        monkeypatch.setattr("app.models.db.session.add", session_add)
        # noinspection PyArgumentList
        user = User(
            username=user_test_object.username, email=user_test_object.email
        )
        task_test_object = TaskTestObject(
            TASK_ID, TASK_NAME, TASK_DESCRIPTION, user
        )
        app_current_user = user
        app_current_user.get_task_in_progress = lambda _: None  # type: ignore
        app_current_user.username = user_test_object.username
        app_current_user.post = Post.query.get(1)
        monkeypatch.setattr(
            "app.routes.redirect.current_user", app_current_user
        )
        client.get("/redirect/export_posts", follow_redirects=True)

    assert "app.utils.tasks.export_posts" in enqueue.args
    task = session_add.args[0]
    assert task.id == task_test_object.id
    assert task.name == task_test_object.name
    assert task.description == task_test_object.description


@pytest.mark.usefixtures("init_db")
def test_get_tasks_in_progress_no_task(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test getting of a task when one does not exist.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        ADMIN_USER_USERNAME, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD
    )
    with test_app.app_context():
        add_test_objects.add_test_users(user_test_object)
        user = User.query.filter_by(username=ADMIN_USER_USERNAME).first()
        task_test_object = TaskTestObject(
            TASK_ID, TASK_NAME, TASK_DESCRIPTION, user
        )
        add_test_objects.add_test_tasks(task_test_object)
        auth.login(user_test_object)
        monkeypatch.setattr(APP_MODELS_JOB_FETCH, lambda *_, **__: None)
        response = client.get("/")
        assert b"100" in response.data


@pytest.mark.usefixtures("init_db")
def test_get_tasks_in_progress(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test getting of a task when there is a task in the database.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        ADMIN_USER_USERNAME, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD
    )
    rq_job = Recorder()
    rq_job.meta = {"progress": MISC_PROGRESS_INT}  # type: ignore
    monkeypatch.setattr(APP_MODELS_JOB_FETCH, lambda *_, **__: rq_job)
    with test_app.app_context():
        # noinspection DuplicatedCode
        add_test_objects.add_test_users(user_test_object)
        user = User.query.filter_by(username=ADMIN_USER_USERNAME).first()
        task_test_object = TaskTestObject(
            TASK_ID, TASK_NAME, TASK_DESCRIPTION, user
        )
        add_test_objects.add_test_tasks(task_test_object)
        auth.login(user_test_object)
        response = client.get("/")
        assert str(MISC_PROGRESS_INT) in response.data.decode()


@pytest.mark.usefixtures("init_db")
def test_get_tasks_in_progress_error_raised(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test getting of a task when an error is raised: 100%, complete.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        ADMIN_USER_USERNAME, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD
    )

    def _fetch(*_: t.Any, **__: t.Any) -> None:
        raise RedisError("test Redis error")

    monkeypatch.setattr(APP_MODELS_JOB_FETCH, _fetch)
    with test_app.app_context():
        # noinspection DuplicatedCode
        add_test_objects.add_test_users(user_test_object)
        user = User.query.filter_by(username=ADMIN_USER_USERNAME).first()
        task_test_object = TaskTestObject(
            TASK_ID, TASK_NAME, TASK_DESCRIPTION, user
        )
        add_test_objects.add_test_tasks(task_test_object)
        auth.login(user_test_object)
        response = client.get("/")

    assert b"100" in response.data


@pytest.mark.usefixtures("init_db")
def test_export_posts(
    monkeypatch: pytest.MonkeyPatch, add_test_objects: AddTestObjects
) -> None:
    """Test data as sent to user when post export requested.

    :param monkeypatch: Mock patch environment and attributes.
    :param add_test_objects: Add test objects to test database.
    """
    # this needs to imported *after* `monkeypatch.setenv` has patched
    # the environment
    import app.utils.tasks

    # faster than waiting for `mail.record_messages` to sync
    # catch `Message` object passed to `mail.send`
    mail_send = Recorder()
    monkeypatch.setattr("app.utils.mail.mail.send", mail_send)
    monkeypatch.setattr("app.utils.tasks.time.sleep", lambda _: None)
    user_test_object = UserTestObject(
        ADMIN_USER_USERNAME, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD
    )
    post_test_object = PostTestObject(
        POST_TITLE_1, POST_BODY_1, POST_AUTHOR_ID_1, POST_CREATED_1
    )

    # running outside `test_app's` context
    # noinspection PyArgumentList
    test_user = User(
        username=ADMIN_USER_USERNAME,
        password_hash=ADMIN_USER_PASSWORD,
        email=ADMIN_USER_EMAIL,
    )
    db.session.add(test_user)
    db.session.commit()
    add_test_objects.add_test_posts(post_test_object)
    user = User.query.get(1)
    task_test_object = TaskTestObject(
        TASK_ID, TASK_NAME, TASK_DESCRIPTION, user
    )
    add_test_objects.add_test_tasks(task_test_object)
    job = Recorder()
    job.meta = {}  # type: ignore
    job.save_meta = Recorder()  # type: ignore
    job.get_id = lambda: task_test_object.id  # type: ignore
    monkeypatch.setattr("app.utils.tasks.get_current_job", lambda: job)
    app.utils.tasks.export_posts(1)
    outbox = mail_send.args[0]
    post_obj = [
        dict(
            body=post_test_object.body,
            created=str(post_test_object.created),
            edited="None",
            id="1",
            title=post_test_object.title,
            user_id="1",
        )
    ]
    assert outbox.subject == f"[JSS]: Posts by {user_test_object.username}"
    assert outbox.recipients == [user_test_object.email]
    assert user_test_object.username in outbox.html
    assert "Please find attached the archive of your posts" in outbox.html
    attachment = outbox.attachments[0]
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
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test versioning of posts route.

    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        AUTHORIZED_USER_USERNAME,
        AUTHORIZED_USER_EMAIL,
        AUTHORIZED_USER_PASSWORD,
        authorized=True,
        confirmed=True,
    )
    post_test_object = PostTestObject(
        POST_TITLE_V1, POST_BODY_V1, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    add_test_objects.add_test_users(user_test_object)
    add_test_objects.add_test_posts(post_test_object)
    auth.login(user_test_object)
    with test_app.app_context():
        post = Post.query.get(1)
        post.title = POST_TITLE_V2
        post.body = POST_BODY_V2
        db.session.commit()

    assert (
        b"v1" in client.get("/post/1?revision=0", follow_redirects=True).data
    )
    assert (
        b"v2" in client.get("/post/1?revision=01", follow_redirects=True).data
    )


@pytest.mark.usefixtures("init_db")
def test_admin_access_control(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test access to admin console restricted to admin user.

    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    admin_user_test_object = UserTestObject(
        ADMIN_USER_USERNAME,
        ADMIN_USER_EMAIL,
        ADMIN_USER_PASSWORD,
        admin=True,
        confirmed=True,
    )
    regular_user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD, confirmed=True
    )
    add_test_objects.add_test_users(
        admin_user_test_object, regular_user_test_object
    )
    auth.login(admin_user_test_object)
    assert client.get(ADMIN_ROUTE, follow_redirects=True).status_code == 200
    assert (
        client.get(ADMIN_USER_ROUTE, follow_redirects=True).status_code == 200
    )
    client.get(REDIRECT_LOGOUT)
    auth.login(regular_user_test_object)
    assert client.get(ADMIN_ROUTE, follow_redirects=True).status_code == 401
    assert (
        client.get(ADMIN_USER_ROUTE, follow_redirects=True).status_code == 403
    )


@pytest.mark.usefixtures("init_db")
def test_admin_access_without_login(client: FlaskClient) -> None:
    """Asserts that the ``AnonymousUserMixin`` error will not be raised.

    This commit fixes the following error causing app to crash if user
    is not logged in:

        AttributeError:
        'AnonymousUserMixin' object has no attribute 'admin'

    :param client:App's test-client API.
    """
    assert client.get(ADMIN_ROUTE, follow_redirects=True).status_code == 401
    assert (
        client.get(ADMIN_USER_ROUTE, follow_redirects=True).status_code == 403
    )


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
    auth: AuthActions,
    add_test_objects: AddTestObjects,
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

    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    :param method: Method for interacting with route.
    :param data: Data to write to form.
    :param bad_route: Route containing reference to non-existing user.
    """
    admin_user_test_object = UserTestObject(
        ADMIN_USER_USERNAME,
        ADMIN_USER_EMAIL,
        ADMIN_USER_PASSWORD,
        admin=True,
        confirmed=True,
    )
    add_test_objects.add_test_users(admin_user_test_object)
    auth.login(admin_user_test_object)
    response = getattr(client, method)(
        bad_route, data=data, follow_redirects=True
    )
    assert response.status_code == 404


@pytest.mark.usefixtures("init_db")
def test_user_name_change_accessible(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test that even after name-change user is accessible by old name.

    Only valid if the old name has not already been adopted by someone
    else.

    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD, confirmed=True
    )
    add_test_objects.add_test_users(user_test_object)
    auth.login(user_test_object)

    # assert that user's profile is available via profile route
    with test_app.app_context():
        user = User.resolve_all_names(MAIN_USER_USERNAME)
        assert user.id == 1

    response = client.get(f"/profile/{MAIN_USER_USERNAME}")
    assert MAIN_USER_USERNAME in response.data.decode()

    # assert that name change is successful
    client.post(
        PROFILE_EDIT,
        data={"username": OTHER_USER_USERNAME},
        follow_redirects=True,
    )
    with test_app.app_context():
        user = User.resolve_all_names(OTHER_USER_USERNAME)
        assert user.id == 1

    response = client.get(f"/profile/{MAIN_USER_USERNAME}")
    assert response.status_code != 404
    assert OTHER_USER_USERNAME in response.data.decode()

    # assert that user can be referenced by their old username
    # they're new name shows up in their profile page
    # the old username is still attached to the same user id
    with test_app.app_context():
        user = User.resolve_all_names(MAIN_USER_USERNAME)
        assert user.id == 1

    response = client.get(f"/profile/{MAIN_USER_USERNAME}")
    assert OTHER_USER_USERNAME in response.data.decode()

    # assert that od name is now a valid choice for a new user
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME,
        "unique@test.com",
        MAIN_USER_PASSWORD,
        confirmed=True,
    )
    add_test_objects.add_test_users(user_test_object)
    auth.login(user_test_object)

    # assert that user's profile is available via profile route
    with test_app.app_context():
        user = User.resolve_all_names(MAIN_USER_USERNAME)
        assert user.id == 2

    response = client.get(f"/profile/{MAIN_USER_USERNAME}")
    assert MAIN_USER_USERNAME in response.data.decode()

    # assert that name change is successful for second user
    client.post(
        PROFILE_EDIT,
        data={"username": LAST_USER_USERNAME},
        follow_redirects=True,
    )
    with test_app.app_context():
        user = User.resolve_all_names(LAST_USER_USERNAME)
        assert user.id == 2

    response = client.get(f"/profile/{LAST_USER_USERNAME}")
    assert LAST_USER_USERNAME in response.data.decode()

    # assert that the latest user can be referenced by the old username
    # they're new name shows up in their profile page
    # the old username is still attached to the same user id
    with test_app.app_context():
        user = User.resolve_all_names(MAIN_USER_USERNAME)
        assert user.id == 2

    response = client.get(f"/profile/{MAIN_USER_USERNAME}")
    assert response.status_code != 404
    assert LAST_USER_USERNAME in response.data.decode()


@pytest.mark.usefixtures("init_db")
def test_reserved_usernames(
    monkeypatch: pytest.MonkeyPatch, test_app: Flask, auth: AuthActions
) -> None:
    """Test that reserved names behave as taken names would in register.

    :param monkeypatch: Mock patch environment and attributes.
    :param auth: Handle authorization with test app.
    :param test_app: Test ``Flask`` app object.
    """
    monkeypatch.setenv("RESERVED_USERNAMES", "reserved1,reserved2")
    config.init_app(test_app)
    assert test_app.config["RESERVED_USERNAMES"] == ["reserved1", "reserved2"]
    user_test_object = UserTestObject(
        "reserved1", MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    response = auth.register(user_test_object)
    assert b"Username is taken" in response.data
    user_test_object = UserTestObject(
        "reserved2", MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    response = auth.register(user_test_object)
    assert b"Username is taken" in response.data


@pytest.mark.usefixtures("init_db")
def test_versions_update(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test versioning of posts route when passing revision to update.

    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        AUTHORIZED_USER_USERNAME,
        AUTHORIZED_USER_EMAIL,
        AUTHORIZED_USER_PASSWORD,
        authorized=True,
        confirmed=True,
    )
    created_post = PostTestObject(
        POST_TITLE_V1, POST_BODY_V1, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    updated_post = PostTestObject(
        POST_TITLE_V2, POST_BODY_V2, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    add_test_objects.add_test_users(user_test_object)
    add_test_objects.add_test_posts(created_post)
    auth.login(user_test_object)
    client.post(
        UPDATE1, data={"title": updated_post.title, "body": updated_post.body}
    )
    response = client.get("/post/1/update?revision=0", follow_redirects=True)
    assert created_post.title in response.data.decode()
    assert created_post.body in response.data.decode()


@pytest.mark.usefixtures("init_db")
def test_versioning_handle_index_error(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test versioning route when passing to large a revision to update.

    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        AUTHORIZED_USER_USERNAME,
        AUTHORIZED_USER_EMAIL,
        AUTHORIZED_USER_PASSWORD,
        authorized=True,
        confirmed=True,
    )
    created_post = PostTestObject(
        POST_TITLE_V1, POST_BODY_V1, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    add_test_objects.add_test_users(user_test_object)
    add_test_objects.add_test_posts(created_post)
    auth.login(user_test_object)
    assert client.get("/post/1/update?revision=1").status_code == 404


def test_config_copyright(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, test_app: Flask
) -> None:
    """Test parsing of metadata from project root.

    :param tmp_path: Create and return temporary ``Path`` object.
    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test ``Flask`` app object.
    """
    monkeypatch.setattr("os.environ", {})
    license_file = tmp_path / "LICENSE"
    pyproject_toml = tmp_path / "pyproject.toml"
    with open(license_file, "w", encoding="utf-8") as fout:
        fout.write(LICENSE)

    with open(pyproject_toml, "w", encoding="utf-8") as fout:
        fout.write(PYPROJECT_TOML)

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
    :param test_app: Test ``Flask`` app object.
    """
    # with `NAVBAR_HOME` set to False
    monkeypatch.setenv("NAVBAR_HOME", "0")
    config.init_app(test_app)
    assert test_app.config["NAVBAR_HOME"] is False
    response = client.get("/")
    assert (
        '<a class="nav-link" href="/"">Home</a>' not in response.data.decode()
    )

    # with `NAVBAR_HOME` set to True
    monkeypatch.setenv("NAVBAR_HOME", "1")
    config.init_app(test_app)
    assert test_app.config["NAVBAR_HOME"] is True
    response = client.get("/")
    assert (
        '<a class="nav-link" href="/"">Home</a>'
        not in response.data.decode()
        in response.data.decode()
    )


@pytest.mark.usefixtures("init_db")
def test_navbar_user_dropdown_config_switch(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test that the user dropdown appropriately switches on and off.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        ADMIN_USER_USERNAME,
        ADMIN_USER_EMAIL,
        ADMIN_USER_PASSWORD,
        admin=True,
        authorized=True,
        confirmed=True,
    )
    add_test_objects.add_test_users(user_test_object)
    auth.login(user_test_object)

    # test user subgroup when dropdown set to False
    monkeypatch.setenv("NAVBAR_USER_DROPDOWN", "0")
    config.init_app(test_app)
    response = client.get("/")
    assert all(
        i in response.data.decode()
        for i in [
            '<div class="list-group">',
            '<li class="nav-item" href="/admin" title="Console">',
            '<a class="nav-link" href="/admin">',
            "Console",
            '<li class="nav-item" href="/profile/admin" title="Profile">',
            '<a class="nav-link" href="/profile/admin">',
            "Profile",
            '<li class="nav-item" href="/auth/logout" title="Logout">',
            '<a class="nav-link" href="/auth/logout">',
            "Logout",
        ]
    )

    # test user subgroup when dropdown set to True
    monkeypatch.setenv("NAVBAR_USER_DROPDOWN", "1")
    config.init_app(test_app)
    response = client.get("/")
    assert all(
        i in response.data.decode()
        for i in [
            '<ul class="dropdown-menu dropdown-menu-right">',
            '<li class="nav-item" href="/admin" title="Console">',
            '<a class="nav-link" href="/admin">',
            "Console",
            '<li class="nav-item" href="/profile/admin" title="Profile">',
            '<a class="nav-link" href="/profile/admin">',
            "Profile",
            '<li class="nav-item" href="/auth/logout" title="Logout">',
            '<a class="nav-link" href="/auth/logout">',
            "Logout",
        ]
    )


def test_all_routes_covered(test_app: Flask) -> None:
    """Test all routes that need to be tested will be.

    :param test_app: Test ``Flask`` app object.
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
    "code,routes", STATUS_CODE_TO_ROUTE_DEFAULT, ids=[200, 401, 405]
)
def test_static_route_default(
    client: FlaskClient,
    add_test_objects: AddTestObjects,
    interpolate_routes: t.Callable[..., None],
    code: int,
    routes: t.List[str],
):
    """Specifically test all status codes of routes.

    :param client: App's test-client API.
    :param add_test_objects: Add test objects to test database.
    :param interpolate_routes: Interpolate route vars with test values.
    :param code: Status code expected.
    :param routes: List of routes with expected status code.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    post_test_object = PostTestObject(
        POST_TITLE_1, POST_BODY_1, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    add_test_objects.add_test_posts(post_test_object)
    interpolate_routes(routes, 1, 0, MAIN_USER_USERNAME)
    assert all(
        client.get(r, follow_redirects=True).status_code == code
        for r in routes
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
    monkeypatch: pytest.MonkeyPatch, attr, obj, expected_repr
):
    """Test ``MutableMapping`` dunder methods (coverage).

    :param monkeypatch: Mock patch environment and attributes.
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


def test_register_macros(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test "macro" is registered and wrapped with ``Markup``.

    :param monkeypatch: Mock patch environment and attributes.
    """
    monkeypatch.setattr("app.utils.register.RegisterContext", RegisterContext)
    test_tag = tags.div(tags.p(tags.h1("Title")))
    macros = RegisterContext("dom_macros", Markup)

    @macros.register
    def registered_macro() -> html_tag:
        return test_tag

    # the ``register_macros`` function will prefix the key with
    # ``dom_macros_``
    registered = RegisterContext.registered()
    assert registered["dom_macros_registered_macro"]() == Markup(test_tag)


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
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test version dropdown.

    Test all 3 variations of unordered list items.

    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param auth: Handle authorization with test app.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        AUTHORIZED_USER_USERNAME,
        AUTHORIZED_USER_EMAIL,
        AUTHORIZED_USER_PASSWORD,
        authorized=True,
        confirmed=True,
    )
    add_test_objects.add_test_users(user_test_object)
    post_test_object = PostTestObject(
        POST_TITLE_V1, POST_BODY_V1, POST_AUTHOR_ID_1, POST_CREATED_1
    )
    add_test_objects.add_test_posts(post_test_object)
    auth.login(user_test_object)

    # create 3 versions (2 other, apart from the original) for all
    # naming branches
    with test_app.app_context():
        post = Post.query.get(1)
        post.title = POST_TITLE_V2
        post.body = POST_BODY_V2
        db.session.commit()
        post.title = POST_TITLE_V3
        post.body = POST_BODY_V3
        db.session.commit()

    response = client.get("/")
    assert all(
        i in response.data.decode()
        for i in [
            '<a href="/post/1?revision=0">',
            "v1",
            '<a href="/post/1?revision=1">',
            "v2: Previous revision",
            '<a class="current-version-anchor" href="/post/1?revision=2">',
            "v3: This revision",
        ]
    )


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize(
    "route,test_object,method",
    [
        (
            "/",
            PostTestObject(
                POST_TITLE_1, POST_BODY_1, POST_AUTHOR_ID_1, POST_CREATED_1
            ),
            "add_test_posts",
        ),
        (
            f"/profile/{ADMIN_USER_USERNAME}",
            PostTestObject(
                POST_TITLE_1, POST_BODY_1, POST_AUTHOR_ID_1, POST_CREATED_1
            ),
            "add_test_posts",
        ),
        (
            "/user/messages",
            MessageTestObject(
                SENDER_ID, RECIPIENT_ID, MESSAGE_BODY, MESSAGE_CREATED
            ),
            "add_test_messages",
        ),
    ],
    ids=["index", "profile", "messages"],
)
def test_pagination_nav(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
    route: str,
    test_object: TestObject,
    method: str,
) -> None:
    """Test links are rendered when more than one page exists.

    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
    :param add_test_objects: Add test objects to test database.
    """
    # every post apart from the first one will add functionality to the
    # pagination footer navbar
    monkeypatch.setenv("POSTS_PER_PAGE", "1")
    config.init_app(test_app)
    user_test_object_1 = UserTestObject(
        ADMIN_USER_USERNAME,
        ADMIN_USER_EMAIL,
        ADMIN_USER_PASSWORD,
        authorized=True,
        confirmed=True,
    )
    user_test_object_2 = UserTestObject(
        AUTHORIZED_USER_USERNAME,
        AUTHORIZED_USER_EMAIL,
        AUTHORIZED_USER_PASSWORD,
        authorized=True,
        confirmed=True,
    )
    add_test_objects.add_test_users(user_test_object_1, user_test_object_2)
    auth.login(user_test_object_1)
    expected_default = [
        '<li class="page-item disabled">',
        '<a class="page-link" href="#" tabindex="-1">',
        "Previous",
        '<li class="page-item">',
        "?page=2",
        "Next",
    ]
    expected_page_2 = [
        '<li class="page-item disabled">',
        '<a class="page-link" href="#" tabindex="-1">',
        "Previous",
        '<li class="page-item">',
        "?page=1",
        "Next",
    ]

    # add two posts to add an extra page
    getattr(add_test_objects, method)(test_object, test_object)

    response = client.get(route).data.decode()
    assert all(i in response for i in expected_default)

    response = client.get(f"{route}?page=2").data.decode()
    assert all(i in response for i in expected_page_2)


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

    :param client: App's test-client API.
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
    :param test_app: Test ``Flask`` app object.
    :param client: App's test-client API.
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
    :param test_app: Test ``Flask`` app object.
    :param runner: Fixture derived from the ``create_app`` factory.
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

    def _pybabel(_: str, *__: t.Union[str, os.PathLike]) -> None:
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
    :param test_app: Test ``Flask`` app object.
    :param runner: Fixture derived from the ``create_app`` factory.
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

    def _pybabel(_: str, *__: t.Union[str, os.PathLike]) -> None:
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
    :param runner: Fixture derived from the ``create_app`` factory.
    """
    commands = []
    pot_file = tmp_path / MESSAGES_POT
    monkeypatch.setattr(APP_UTILS_LANG_POT_FILE, lambda: pot_file)

    def _subprocess_run(
        args: t.List[t.Union[str, os.PathLike]], **_: bool
    ) -> None:
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
    :param runner: Fixture derived from the ``create_app`` factory.
    """
    commands = []
    pot_file = tmp_path / MESSAGES_POT
    monkeypatch.setattr(APP_UTILS_LANG_POT_FILE, lambda: pot_file)

    def _subprocess_run(
        args: t.List[t.Union[str, os.PathLike]], **_: bool
    ) -> None:
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
    :param test_app: Test ``Flask`` app object.
    :param runner: Fixture derived from the ``create_app`` factory.
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

    :param test_app: Test ``Flask`` app object.
    """
    with test_app.app_context():
        assert lang._pot_file() == Path(MESSAGES_POT)
