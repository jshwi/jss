"""
tests._test
===========
"""
# pylint: disable=too-many-arguments,too-many-lines,too-many-locals
# pylint: disable=import-outside-toplevel,protected-access
from __future__ import annotations

import fnmatch
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

from app import config
from app.extensions import mail
from app.extensions.talisman import ContentSecurityPolicy, CSPType
from app.log import smtp_handler
from app.models import Post, User, db

from .const import (
    ADMIN,
    ADMIN_ROUTE,
    ADMIN_USER_EMAIL,
    ADMIN_USER_PASSWORD,
    ADMIN_USER_ROUTE,
    ADMIN_USER_USERNAME,
    APP_UTILS_LANG_SUBPROCESS_RUN,
    AUTHORIZED_USER_EMAIL,
    AUTHORIZED_USER_PASSWORD,
    AUTHORIZED_USER_USERNAME,
    BODY,
    COMPILE,
    COPYRIGHT_AUTHOR,
    COPYRIGHT_EMAIL,
    COPYRIGHT_YEAR,
    COVERED_ROUTES,
    CREATE,
    FILE,
    INIT,
    INIT_DB,
    INVALID_OR_EXPIRED,
    LAST_USER_EMAIL,
    LAST_USER_PASSWORD,
    LAST_USER_USERNAME,
    LICENSE,
    LICENSE_CONTENTS,
    LOCATION,
    LOGOUT,
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
    NAVBAR_HOME,
    OTHER_USER_EMAIL,
    OTHER_USER_PASSWORD,
    OTHER_USER_USERNAME,
    POST,
    POST_1,
    POST_1_DELETE,
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
    POST_CREATE,
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
    PYBABEL,
    PYPROJECT_TOML,
    RECIPIENT_ID,
    REDIRECT_LOGOUT,
    ROUTE,
    SENDER_ID,
    STATUS_CODE_TO_ROUTE_DEFAULT,
    TITLE,
    TRANSLATE,
    TRANSLATIONS_DIR,
    TUX_PNG,
    UPDATE1,
    UPLOAD_FAVICON,
    USER,
    USERNAME,
    USERNAME_IS_TAKEN,
)
from .utils import (
    AddTestObjects,
    AuthActions,
    MessageTestObject,
    PostTestObject,
    Recorder,
    TestObject,
    UserTestObject,
)


@pytest.mark.usefixtures(INIT_DB)
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

    :param test_app: Test application.
    :param client: Test application client.
    :param auth: Handle authorization.
    """
    assert client.get("/auth/register").status_code == 200
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    response = auth.register(user_test_object)
    assert response.headers[LOCATION] == "/auth/unconfirmed"
    with test_app.app_context():
        user = User.query.filter_by(username=user_test_object.username).first()
        assert user is not None


@pytest.mark.usefixtures(INIT_DB)
def test_login(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test login functionality.

    :param client: Test application client.
    :param auth: Handle authorization.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    response = auth.login(user_test_object)
    assert response.headers[LOCATION] == "/auth/unconfirmed"
    with client:
        client.get("/")
        assert current_user.username == user_test_object.username


@pytest.mark.usefixtures(INIT_DB)
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

    :param auth: Handle authorization.
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


@pytest.mark.usefixtures(INIT_DB)
def test_logout(client: FlaskClient, auth: AuthActions) -> None:
    """Test logout functionality.

    :param client: Test application client.
    :param auth: Handle authorization.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    auth.login(user_test_object)
    with client:
        client.get(REDIRECT_LOGOUT)
        assert "user_id" not in session


@pytest.mark.usefixtures(INIT_DB)
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

    :param client: Test application client.
    :param auth: Handle authorization.
    :param add_test_objects: Add test objects to test database.
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
    assert LOGOUT in decoded_response
    assert post_test_object.title in decoded_response
    assert user_test_object.username in decoded_response
    assert post_test_object.body in decoded_response
    assert 'href="/post/1/update"' in decoded_response


@pytest.mark.parametrize(ROUTE, [POST_CREATE, UPDATE1, POST_1_DELETE])
def test_login_required(client: FlaskClient, route: str) -> None:
    """Test requirement that user be logged in to post.

    A user must be logged in to access the CREATE, "update", and
    "delete" views.

    The logged-in user must be the author of the post to access the
    update and delete views, otherwise a ``403 Forbidden`` status is
    returned.

    :param client: Test application client.
    :param route: Parametrized route path.
    """
    response = client.post(route, follow_redirects=True)
    assert response.status_code == 401


@pytest.mark.usefixtures(INIT_DB)
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

    :param test_app: Test application.
    :param client: Test application client.
    :param auth: Handle authorization.
    :param add_test_objects: Add test objects to test database.
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
    assert client.post(POST_1_DELETE).status_code == 403

    # current user doesn't see edit link
    assert b'href="/post/1/update"' not in client.get("/").data
    response = client.get("/post/1")
    assert b'href="/post/1/update?revision=-1"' not in response.data


@pytest.mark.usefixtures(INIT_DB)
@pytest.mark.parametrize(ROUTE, ["/2/update", "/2/delete"])
def test_exists_required(
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
    route: str,
) -> None:
    """Test ``404 Not Found`` is returned when a route does not exist.

    :param client: Test application client.
    :param auth: Handle authorization.
    :param add_test_objects: Add test objects to test database.
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


@pytest.mark.usefixtures(INIT_DB)
def test_create(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test create view functionality.

    When valid data is sent in a ``POST`` request the create view should
    insert the new post data into the database.

    :param test_app: Test application.
    :param client: Test application client.
    :param auth: Handle authorization.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        AUTHORIZED_USER_USERNAME,
        AUTHORIZED_USER_EMAIL,
        AUTHORIZED_USER_PASSWORD,
        authorized=True,
    )
    add_test_objects.add_test_users(user_test_object)
    auth.login(user_test_object)
    assert client.get(POST_CREATE).status_code == 200
    client.post(POST_CREATE, data={TITLE: POST_TITLE_1, BODY: POST_BODY_1})
    with test_app.app_context():
        count = Post.query.count()
        assert count == 1


@pytest.mark.usefixtures(INIT_DB)
def test_update(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test update view modifies the existing data.

    :param test_app: Test application.
    :param client: Test application client.
    :param auth: Handle authorization.
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
        UPDATE1, data={TITLE: updated_post.title, BODY: updated_post.body}
    )
    with test_app.app_context():
        post = Post.query.get(1)
        assert post.title == updated_post.title
        assert post.body == updated_post.body

    assert "Edited" in client.get(POST_1).data.decode()


@pytest.mark.usefixtures(INIT_DB)
def test_delete(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test deletion of posts.

    The "delete" view should redirect to the index URl and the post
    should no longer exist in the database.

    :param test_app: Test application.
    :param client: Test application client.
    :param auth: Handle authorization.
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
    response = client.post(POST_1_DELETE)
    assert response.headers[LOCATION] == "/"
    with test_app.app_context():
        post = Post.query.get(1)
        assert post is None


def test_create_command(
    monkeypatch: pytest.MonkeyPatch, runner: FlaskCliRunner
) -> None:
    """Test cli.

    :param monkeypatch: Mock patch environment and attributes.
    :param runner: Test application cli.
    """
    # flask create user
    state_1 = Recorder()
    monkeypatch.setattr("app.cli.create.create_user_cli", state_1)
    runner.invoke(args=[CREATE, USER])
    assert state_1.called

    # flask create admin
    state_2 = Recorder()
    monkeypatch.setattr("app.cli.create.create_admin_cli", state_2)
    runner.invoke(args=[CREATE, ADMIN])
    assert state_2.called


def test_export() -> None:
    """Test export to dict_ function for models."""
    # noinspection PyArgumentList
    post = Post(title=POST_TITLE_1, body=POST_BODY_1, created=POST_CREATED_1)
    as_dict = post.export()
    assert as_dict["title"] == POST_TITLE_1
    assert as_dict[BODY] == POST_BODY_1
    assert as_dict["created"] == str(POST_CREATED_1)


@pytest.mark.usefixtures(INIT_DB)
def test_create_user_no_exist(
    test_app: Flask,
    runner: FlaskCliRunner,
    patch_getpass: t.Callable[[t.List[str]], None],
) -> None:
    """Test creation of a new user that doesn't exist.

    :param test_app: Test application.
    :param runner: Test application cli.
    :param patch_getpass: Patch ``getpass`` password module.
    """
    user_input = f"{MAIN_USER_USERNAME}\n{MAIN_USER_EMAIL}\n"
    patch_getpass([MAIN_USER_PASSWORD, MAIN_USER_PASSWORD])
    response = runner.invoke(args=[CREATE, USER], input=user_input)
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
    ids=[USERNAME, "email"],
)
@pytest.mark.usefixtures(INIT_DB)
def test_create_user_exists(
    runner: FlaskCliRunner,
    add_test_objects: AddTestObjects,
    username: str,
    email: str,
    expected: str,
) -> None:
    """Test creation of a new user that exists.

    :param runner: Test application cli.
    :param add_test_objects: Add test objects to test database.
    :param username: The test user username.
    :param email: The test user email.
    :param expected: Expected result.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    response = runner.invoke(
        args=[CREATE, USER], input=f"{username}\n{email}\n"
    )
    assert expected in response.output


@pytest.mark.usefixtures(INIT_DB)
def test_create_user_email_exists(
    runner: FlaskCliRunner, add_test_objects: AddTestObjects
) -> None:
    """Test creation of a new user whose email is already registered.

    :param runner: Test application cli.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    user_input = f"{OTHER_USER_EMAIL}\n{MAIN_USER_EMAIL}"
    add_test_objects.add_test_users(user_test_object)
    response = runner.invoke(args=[CREATE, USER], input=user_input)
    assert (
        "a user with this email address is already registered"
        in response.output
    )


@pytest.mark.usefixtures(INIT_DB)
def test_create_user_passwords_no_match(
    runner: FlaskCliRunner, patch_getpass: t.Callable[[t.List[str]], None]
) -> None:
    """Test creation of a new user where passwords don't match.

    :param runner: Test application cli.
    :param patch_getpass: Patch ``getpass`` password module.
    """
    user_input = f"{MAIN_USER_USERNAME}\n{MAIN_USER_EMAIL}\n"
    patch_getpass([MAIN_USER_PASSWORD, OTHER_USER_PASSWORD])
    response = runner.invoke(args=[CREATE, USER], input=user_input)
    assert "passwords do not match: could not add user" in response.output


@pytest.mark.usefixtures(INIT_DB)
def test_create_admin(test_app: Flask, runner: FlaskCliRunner) -> None:
    """Test commands called when invoking ``flask create admin``.

    :param test_app: Test application.
    :param runner: Test application cli.
    """
    response = runner.invoke(args=[CREATE, ADMIN])
    assert "admin successfully created" in response.output
    with test_app.app_context():
        admin = User.query.filter_by(username=ADMIN).first()
        assert admin.email == test_app.config["ADMINS"][0]
        assert admin.check_password(ADMIN_USER_PASSWORD)


def test_404_error(client: FlaskClient) -> None:
    """Test ``404 Not Found`` is returned when a route does not exist.

    :param client: Test application client.
    """
    response = client.post("/does_not_exist")
    assert response.status_code == 404


@pytest.mark.usefixtures(INIT_DB)
@pytest.mark.parametrize(ROUTE, [POST_CREATE, UPDATE1, POST_1_DELETE])
def test_admin_required(
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
    route: str,
) -> None:
    """Test requirement that admin user be logged in to post.

    An admin user must be logged in to access the CREATE, "update",
    and "delete" views.

    The logged-in user must be the author of the post to access the
    update and delete views, otherwise a ``403 Forbidden`` status is
    returned.

    :param client: Test application client.
    :param auth: Handle authorization.
    :param add_test_objects: Add test objects to test database.
    :param route: Parametrized route path.
    """
    user_test_object = UserTestObject(
        ADMIN_USER_USERNAME, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD, admin=False
    )
    add_test_objects.add_test_users(user_test_object)
    auth.login(user_test_object)
    response = client.post(route, follow_redirects=True)
    assert response.status_code == 401


@pytest.mark.usefixtures(INIT_DB)
@pytest.mark.parametrize(
    "username,email,message",
    [
        (MAIN_USER_USERNAME, OTHER_USER_EMAIL, USERNAME_IS_TAKEN),
        (OTHER_USER_USERNAME, MAIN_USER_EMAIL, b"already registered"),
    ],
    ids=[USERNAME, "email"],
)
def test_register_invalid_fields(
    auth: AuthActions,
    add_test_objects: AddTestObjects,
    username: str,
    email: str,
    message: str,
) -> None:
    """Test different invalid input and error messages.

    :param auth: Handle authorization.
    :param add_test_objects: Add test objects to test database.
    :param username: The test user username.
    :param email: The test user email.
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


@pytest.mark.usefixtures(INIT_DB)
def test_confirmation_email_unconfirmed(
    test_app: Flask, client: FlaskClient, auth: AuthActions
) -> None:
    """Test user is moved from confirmed as False to True.

    :param test_app: Test application.
    :param client: Test application client.
    :param auth: Handle authorization.
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


@pytest.mark.usefixtures(INIT_DB)
def test_confirmation_email_confirmed(
    test_app: Flask, auth: AuthActions
) -> None:
    """Test user redirected when already confirmed.

    :param test_app: Test application.
    :param auth: Handle authorization.
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


@pytest.mark.usefixtures(INIT_DB)
def test_login_confirmed(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test login functionality once user is verified.

    :param test_app: Test application.
    :param client: Flask client testing helper.
    :param auth: Handle authorization.
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
    assert response.headers[LOCATION] == "/"
    with client:
        client.get("/")
        assert current_user.username == user_test_object.username


@pytest.mark.usefixtures(INIT_DB)
def test_confirmation_email_resend(
    client: FlaskClient, auth: AuthActions
) -> None:
    """Test user receives email when requesting resend.

    :param client: Test application client.
    :param auth: Handle authorization.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    auth.register(user_test_object)
    response = client.get("/redirect/resend", follow_redirects=True)
    assert b"A new confirmation email has been sent." in response.data


@pytest.mark.usefixtures(INIT_DB)
def test_request_password_reset_email(
    auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test that the correct email is sent to user for password reset.

    :param auth: Handle authorization.
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


@pytest.mark.usefixtures(INIT_DB)
def test_bad_token(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test user denied when jwt for resetting password is expired.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param auth: Handle authorization.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    with test_app.app_context():
        with mail.record_messages() as outbox:
            monkeypatch.setattr(
                "app.views.auth.generate_reset_password_token",
                lambda *_, **__: "bad_token",
            )
            auth.request_password_reset(MAIN_USER_EMAIL, follow_redirects=True)

        response = auth.follow_token_route(
            outbox[0].html, follow_redirects=True
        )
        assert INVALID_OR_EXPIRED in response.data.decode()


@pytest.mark.usefixtures(INIT_DB)
def test_email_does_not_exist(auth: AuthActions) -> None:
    """Test user notified when email does not exist for password reset.

    :param auth: Handle authorization.
    """
    response = auth.request_password_reset(MAIN_USER_EMAIL)
    assert b"An account with that email address doesn't exist" in response.data


@pytest.mark.usefixtures(INIT_DB)
def test_redundant_token(
    test_app: Flask, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test user notified that them being logged in has voided token.

    :param test_app: Test application.
    :param auth: Handle authorization.
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


@pytest.mark.usefixtures(INIT_DB)
def test_reset_password(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test the password reset process.

    :param test_app: Test application.
    :param client: Test application client.
    :param auth: Handle authorization.
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


@pytest.mark.usefixtures(INIT_DB)
def test_profile_page(
    client: FlaskClient, add_test_objects: AddTestObjects
) -> None:
    """Test response when visiting profile page of existing user.

    :param client: Test application client.
    :param add_test_objects: Add test objects to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_objects.add_test_users(user_test_object)
    response = client.get(f"/profile/{MAIN_USER_USERNAME}")
    assert b'src="https://gravatar.com/avatar/' in response.data


@pytest.mark.usefixtures(INIT_DB)
def test_post_page(
    client: FlaskClient, add_test_objects: AddTestObjects
) -> None:
    """Test for correct contents in post page response.

    :param client: Test application client.
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


@pytest.mark.usefixtures(INIT_DB)
def test_edit_profile(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test edit profile page.

    :param client: Test application client.
    :param auth: Handle authorization.
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
        data={USERNAME: OTHER_USER_USERNAME, "about_me": "testing about me"},
        follow_redirects=True,
    )
    assert OTHER_USER_USERNAME in response.data.decode()
    assert b"testing about me" in response.data


@pytest.mark.usefixtures(INIT_DB)
def test_unconfirmed(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test when unconfirmed user tries to enter restricted view.

    :param client: Test application client.
    :param auth: Handle authorization.
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


@pytest.mark.usefixtures(INIT_DB)
def test_follow(test_app: Flask, add_test_objects: AddTestObjects) -> None:
    """Test functionality of user follows.

    :param test_app: Test application.
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


@pytest.mark.usefixtures(INIT_DB)
def test_follow_posts(
    test_app: Flask, add_test_objects: AddTestObjects
) -> None:
    """Test functionality of post follows.

    :param test_app: Test application.
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


@pytest.mark.usefixtures(INIT_DB)
def test_post_follow_unfollow_routes(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test ``POST`` request to follow and unfollow a user.

    :param client: Test application client.
    :param auth: Handle authorization.
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


@pytest.mark.usefixtures(INIT_DB)
def test_send_message(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test sending of personal messages from one user to another.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param client: Test application client.
    :param auth: Handle authorization.
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
    ]:
        assert i in response.data.decode()

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


@pytest.mark.usefixtures(INIT_DB)
def test_versions(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test versioning of posts route.

    :param test_app: Test application.
    :param client: Test application client.
    :param auth: Handle authorization.
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


@pytest.mark.usefixtures(INIT_DB)
def test_admin_access_control(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test access to admin console restricted to admin user.

    :param client: Test application client.
    :param auth: Handle authorization.
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


@pytest.mark.usefixtures(INIT_DB)
def test_admin_access_without_login(client: FlaskClient) -> None:
    """Asserts that the ``AnonymousUserMixin`` error will not be raised.

    This commit fixes the following error causing app to crash if user
    is not logged in:

        AttributeError:
        'AnonymousUserMixin' object has no attribute 'admin'

    :param client: Test application client.
    """
    assert client.get(ADMIN_ROUTE, follow_redirects=True).status_code == 401
    assert (
        client.get(ADMIN_USER_ROUTE, follow_redirects=True).status_code == 403
    )


@pytest.mark.usefixtures(INIT_DB)
@pytest.mark.parametrize(
    "method,data,bad_route",
    [
        ("get", {}, "profile/noname"),
        (POST, {}, "follow/noname"),
        (POST, {}, "unfollow/noname"),
        (POST, {"message": "testing"}, "send_message/noname"),
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

    :param client: Test application client.
    :param auth: Handle authorization.
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


@pytest.mark.usefixtures(INIT_DB)
def test_user_name_change_accessible(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test that even after name-change user is accessible by old name.

    Only valid if the old name has not already been adopted by someone
    else.

    :param test_app: Test application.
    :param client: Test application client.
    :param auth: Handle authorization.
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
        data={USERNAME: OTHER_USER_USERNAME},
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
        data={USERNAME: LAST_USER_USERNAME},
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


@pytest.mark.usefixtures(INIT_DB)
def test_reserved_usernames(
    monkeypatch: pytest.MonkeyPatch, test_app: Flask, auth: AuthActions
) -> None:
    """Test that reserved names behave as taken names would in register.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param auth: Handle authorization.
    """
    monkeypatch.setenv("RESERVED_USERNAMES", "reserved1,reserved2")
    config.init_app(test_app)
    assert test_app.config["RESERVED_USERNAMES"] == ["reserved1", "reserved2"]
    user_test_object = UserTestObject(
        "reserved1", MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    response = auth.register(user_test_object)
    assert USERNAME_IS_TAKEN in response.data
    user_test_object = UserTestObject(
        "reserved2", MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    response = auth.register(user_test_object)
    assert USERNAME_IS_TAKEN in response.data


@pytest.mark.usefixtures(INIT_DB)
def test_versions_update(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test versioning of posts route when passing revision to update.

    :param client: Test application client.
    :param auth: Handle authorization.
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
        UPDATE1, data={TITLE: updated_post.title, BODY: updated_post.body}
    )
    response = client.get("/post/1/update?revision=0", follow_redirects=True)
    assert created_post.title in response.data.decode()
    assert created_post.body in response.data.decode()


@pytest.mark.usefixtures(INIT_DB)
def test_versioning_handle_index_error(
    client: FlaskClient, auth: AuthActions, add_test_objects: AddTestObjects
) -> None:
    """Test versioning route when passing to large a revision to update.

    :param client: Test application client.
    :param auth: Handle authorization.
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
    :param test_app: Test application.
    """
    pyproject_toml = tmp_path / "pyproject.toml"
    with open(os.environ["LICENSE"], "w", encoding="utf-8") as fout:
        fout.write(LICENSE_CONTENTS)

    with open(pyproject_toml, "w", encoding="utf-8") as fout:
        fout.write(PYPROJECT_TOML)

    monkeypatch.setenv("PYPROJECT_TOML", str(pyproject_toml))
    config.init_app(test_app)
    assert str(test_app.config[LICENSE]) == os.environ["LICENSE"]
    assert test_app.config["COPYRIGHT_YEAR"] == COPYRIGHT_YEAR
    assert test_app.config["COPYRIGHT_AUTHOR"] == COPYRIGHT_AUTHOR
    assert test_app.config["COPYRIGHT_EMAIL"] == COPYRIGHT_EMAIL


@pytest.mark.usefixtures(INIT_DB)
def test_navbar_home_config_switch(
    monkeypatch: pytest.MonkeyPatch, test_app: Flask, client: FlaskClient
) -> None:
    """Test that the navbar Home link appropriately switches on and off.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param client: Test application client.
    """
    # with `NAVBAR_HOME` set to False
    monkeypatch.setenv(NAVBAR_HOME, "0")
    config.init_app(test_app)
    assert test_app.config[NAVBAR_HOME] is False
    response = client.get("/")
    assert (
        '<a class="nav-link" href="/"">Home</a>' not in response.data.decode()
    )

    # with `NAVBAR_HOME` set to True
    monkeypatch.setenv(NAVBAR_HOME, "1")
    config.init_app(test_app)
    assert test_app.config[NAVBAR_HOME] is True
    response = client.get("/")
    assert (
        '<a class="nav-link" href="/"">Home</a>'
        not in response.data.decode()
        in response.data.decode()
    )


@pytest.mark.usefixtures(INIT_DB)
def test_navbar_user_dropdown_config_switch(
    monkeypatch: pytest.MonkeyPatch,
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test that the user dropdown appropriately switches on and off.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param client: Test application client.
    :param auth: Handle authorization.
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
            '<div class="list-group list-group-horizontal">',
            '<li class="nav-item" href="/database" title="Database">',
            '<a class="nav-link" href="/database">',
            "Database",
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
            '<li class="nav-item" href="/database" title="Database">',
            '<a class="nav-link" href="/database">',
            "Database",
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

    :param test_app: Test application.
    """
    ignore = ["/database/*", "/static/*", "/bootstrap/*"]
    exception = ["/database/"]
    filter_covered = [
        r.rule
        for r in test_app.url_map.iter_rules()
        if not any(fnmatch.fnmatch(r.rule, i) for i in ignore)
        or r.rule in exception
    ]
    assert "/database/database_notification/ajax/lookup/" not in filter_covered
    assert "/database/" in filter_covered
    for route in filter_covered:
        assert route in COVERED_ROUTES


@pytest.mark.usefixtures(INIT_DB, "init_static")
@pytest.mark.parametrize(
    "code,routes", STATUS_CODE_TO_ROUTE_DEFAULT, ids=[200, 401, 405]
)
def test_static_route_default(
    client: FlaskClient,
    add_test_objects: AddTestObjects,
    interpolate_routes: t.Callable[..., None],
    code: int,
    routes: t.List[str],
) -> None:
    """Specifically test all status codes of routes.

    :param client: Test application client.
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
    for route in routes:
        assert client.get(route, follow_redirects=True).status_code == code


@pytest.mark.usefixtures(INIT_DB)
def test_version_dropdown(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_objects: AddTestObjects,
) -> None:
    """Test version dropdown.

    Test all 3 variations of unordered list items.

    :param test_app: Test application.
    :param client: Test application client.
    :param auth: Handle authorization.
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
    for i in [
        '<a href="/post/1?revision=0">',
        "v1",
        '<a href="/post/1?revision=1">',
        "v2: Previous revision",
        '<a class="current-version-anchor" href="/post/1?revision=2">',
        "v3: This revision",
    ]:
        assert i in response.data.decode()


@pytest.mark.usefixtures(INIT_DB)
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
    test_object: TestObject,
    add_test_objects: AddTestObjects,
    route: str,
    method: str,
) -> None:
    """Test links are rendered when more than one page exists.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param client: Test application client.
    :param auth: Handle authorization.
    :param test_object: Base object for test objects.
    :param add_test_objects: Add test objects to test database.
    :param route: Route to test pagination with.
    :param method: Method to test pagination with.
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


@pytest.mark.usefixtures(INIT_DB)
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
            "app.views.report.current_app.logger.info", captured
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
def test_csp_class(
    monkeypatch: pytest.MonkeyPatch,
    default: CSPType,
    add: CSPType,
    expected: CSPType,
) -> None:
    """Test the ``ContentSecurityPolicy`` object.

    Test the assigning of a default policy, and the addition of any
    custom configured policy items.

    :param monkeypatch: Mock patch environment and attributes.
    :param default: The policy to start with.
    :param add: The configured policy directive to add to the existing
        policy.
    :param expected: The expected
    """
    monkeypatch.setattr("json.loads", lambda _: default)
    csp = ContentSecurityPolicy()
    csp.update_policy(add)
    assert dict(csp) == expected  # type: ignore


def test_jinja2_required_extensions() -> None:
    """Test ``jinja2.ext`` has attrs needed for language support."""
    assert hasattr(jinja2_ext, "autoescape")
    assert hasattr(jinja2_ext, "with_")


# noinspection DuplicatedCode
def test_translate_init_files(
    monkeypatch: pytest.MonkeyPatch, test_app: Flask, runner: FlaskCliRunner
) -> None:
    """Test management of files when running ``flask translate init``.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param runner: Test application cli.
    """
    tdir: Path = test_app.config[TRANSLATIONS_DIR]
    lang_arg = "es"
    lc_dir = tdir / lang_arg / "LC_MESSAGES"
    po_file = lc_dir / MESSAGES_PO

    def _extract():
        Path(MESSAGES_POT).write_text(POT_CONTENTS)

    def _init():
        lc_dir.mkdir(parents=True)
        shutil.copy2(MESSAGES_POT, po_file)

    commands = [_extract, _init]

    def _run(_: str, *__: str | os.PathLike, **___: bool) -> None:
        commands.pop(0)()

    monkeypatch.setattr("app.cli.translate.subprocess.run", _run)
    result = runner.invoke(
        args=[TRANSLATE, INIT, lang_arg], catch_exceptions=False
    )
    po_contents = po_file.read_text(encoding="utf-8")
    assert "<Result okay>" in str(result)
    assert POT_CONTENTS[-3:] == '"\n\n'
    assert not Path(MESSAGES_POT).is_file()
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
    monkeypatch: pytest.MonkeyPatch, test_app: Flask, runner: FlaskCliRunner
) -> None:
    """Test management of files when running ``flask translate update``.

    :param monkeypatch: Mock patch environment and attributes.
    :param test_app: Test application.
    :param runner: Test application cli.
    """
    tdir: Path = test_app.config[TRANSLATIONS_DIR]
    lang_arg = "es"
    lc_dir = tdir / lang_arg / "LC_MESSAGES"
    po_file = lc_dir / MESSAGES_PO

    def _extract():
        Path(MESSAGES_POT).write_text(POT_CONTENTS)

    def _init():
        lc_dir.mkdir(parents=True)
        shutil.copy2(Path(MESSAGES_POT), po_file)

    def _update():
        shutil.copy2(Path(MESSAGES_POT), po_file)

    _extract()
    _init()
    os.remove(Path(MESSAGES_POT))

    commands = [_extract, _update]

    def _run(_: str, *__: str | os.PathLike, **___: bool) -> None:
        commands.pop(0)()

    monkeypatch.setattr("app.cli.translate.subprocess.run", _run)
    result = runner.invoke(args=[TRANSLATE, "update"], catch_exceptions=False)
    po_contents = po_file.read_text(encoding="utf-8")
    assert "<Result okay>" in str(result)
    assert POT_CONTENTS[-3:] == '"\n\n'
    assert not Path(MESSAGES_POT).is_file()
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
    monkeypatch: pytest.MonkeyPatch, runner: FlaskCliRunner
) -> None:
    """Test commands called when invoking ``flask translate init``.

    :param monkeypatch: Mock patch environment and attributes.
    :param runner: Test application cli.
    """
    commands = []

    def _subprocess_run(args: t.List[str | os.PathLike], **_: bool) -> None:
        commands.extend(args)
        Path(MESSAGES_POT).write_text(POT_CONTENTS)

    monkeypatch.setattr(APP_UTILS_LANG_SUBPROCESS_RUN, _subprocess_run)
    runner.invoke(args=[TRANSLATE, INIT, "es"])
    assert PYBABEL in commands
    assert "extract" in commands
    assert INIT in commands


# noinspection DuplicatedCode
def test_translate_update_args(
    monkeypatch: pytest.MonkeyPatch, runner: FlaskCliRunner
) -> None:
    """Test commands called when invoking ``flask translate update``.

    :param monkeypatch: Mock patch environment and attributes.
    :param runner: Test application cli.
    """
    commands = []

    def _subprocess_run(args: t.List[str | os.PathLike], **_: bool) -> None:
        commands.extend(args)
        Path(MESSAGES_POT).write_text(POT_CONTENTS)

    monkeypatch.setattr(APP_UTILS_LANG_SUBPROCESS_RUN, _subprocess_run)
    runner.invoke(args=[TRANSLATE, "update"])
    assert PYBABEL in commands
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
        test_app.config[TRANSLATIONS_DIR] / "es" / "LC_MESSAGES" / MESSAGES_PO
    )
    commands = []
    monkeypatch.setattr(
        APP_UTILS_LANG_SUBPROCESS_RUN, lambda x, **y: commands.extend(x)
    )
    result = runner.invoke(args=[TRANSLATE, COMPILE], catch_exceptions=False)
    assert "No message catalogs to compile" in result.output
    assert not commands
    po_file.parent.mkdir(parents=True)
    po_file.touch()
    runner.invoke(args=[TRANSLATE, COMPILE], catch_exceptions=False)
    assert PYBABEL in commands
    assert COMPILE in commands


def test_has_languages(test_app: Flask) -> None:
    """Test languages collected for config property.

    :param test_app: Test application.
    """
    shutil.copytree(
        Path(__file__).parent.parent / "app" / "translations",
        os.environ["TRANSLATIONS_DIR"],
    )
    config.init_app(test_app)
    assert "es" in test_app.config["LANGUAGES"]


def test_book_call(
    monkeypatch: pytest.MonkeyPatch, client: FlaskClient
) -> None:
    """Test booking of call.

    :param monkeypatch: Mock patch environment and attributes.
    :param client: Test application client.
    """
    stripe = Recorder()
    stripe.checkout = Recorder()  # type: ignore
    stripe.checkout.Session = Recorder()  # type: ignore
    stripe.checkout.Session.create = Recorder()  # type: ignore
    stripe.checkout.Session.create.url = Recorder()  # type: ignore
    monkeypatch.setattr("app.views.order.stripe", stripe)
    client.post("/order/call")
    assert (
        stripe.checkout.Session.create.kwargs["api_key"]  # type: ignore
        == "stripe_secret_key"
    )
    assert (
        stripe.checkout.Session.create.kwargs["line_items"][0][  # type: ignore
            "price_data"
        ]["unit_amount"]
        == 20000
    )


@pytest.mark.usefixtures(INIT_DB)
def test_order_success(client: FlaskClient) -> None:
    """Test order success view.

    :param client: Test application client.
    """
    response = client.get("/order/success", follow_redirects=True)
    assert "Thank you, your order has been placed." in response.data.decode()


@pytest.mark.usefixtures(INIT_DB)
def test_order_cancel(client: FlaskClient) -> None:
    """Test order cancellation view.

    :param client: Test application client.
    """
    response = client.get("/order/cancel", follow_redirects=True)
    assert "Your order was canceled." in response.data.decode()


@pytest.mark.usefixtures(INIT_DB)
def test_admin_page(client: FlaskClient) -> None:
    """Test rendering of admin page.

    :param client: Test application client.
    """
    response = client.get("/admin/")
    assert "Admin" in response.data.decode()


@pytest.mark.usefixtures(INIT_DB)
def test_upload_view(
    client: FlaskClient, add_test_objects: AddTestObjects, auth: AuthActions
) -> None:
    """Test upload create view.

    :param client: Test application client.
    :param add_test_objects: Add test objects to test database.
    :param auth: Handle authorization.
    """
    user_test_object = UserTestObject(
        ADMIN_USER_USERNAME, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD, admin=True
    )
    add_test_objects.add_test_users(user_test_object)
    auth.login(user_test_object)
    response = client.get(UPLOAD_FAVICON, follow_redirects=True)
    assert "Upload favicon" in response.data.decode()


@pytest.mark.usefixtures(INIT_DB)
def test_upload_good_file(
    client: FlaskClient, add_test_objects: AddTestObjects, auth: AuthActions
) -> None:
    """Test uploading of a valid file.

    :param client: Test application client.
    :param add_test_objects: Add test objects to test database.
    :param auth: Handle authorization.
    """
    user_test_object = UserTestObject(
        ADMIN_USER_USERNAME, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD, admin=True
    )
    add_test_objects.add_test_users(user_test_object)
    auth.login(user_test_object)
    response = client.post(
        UPLOAD_FAVICON, follow_redirects=True, data={FILE: TUX_PNG.open("rb")}
    )
    assert f"{TUX_PNG.name} uploaded successfully" in response.data.decode()


# noinspection DuplicatedCode
@pytest.mark.usefixtures(INIT_DB)
def test_upload_bad_file(
    tmp_path: Path,
    client: FlaskClient,
    add_test_objects: AddTestObjects,
    auth: AuthActions,
) -> None:
    """Test uploading of an invalid file.

    :param tmp_path: Create and return temporary ``Path`` object.
    :param client: Test application client.
    :param add_test_objects: Add test objects to test database.
    :param auth: Handle authorization.
    """
    file = tmp_path / f"{TUX_PNG.stem}.txt"
    shutil.copy(TUX_PNG, file)
    user_test_object = UserTestObject(
        ADMIN_USER_USERNAME, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD, admin=True
    )
    add_test_objects.add_test_users(user_test_object)
    auth.login(user_test_object)
    response = client.post(
        UPLOAD_FAVICON, follow_redirects=True, data={FILE: file.open("rb")}
    )
    assert "cannot confirm validity of file" in response.data.decode()


# noinspection DuplicatedCode
@pytest.mark.usefixtures(INIT_DB)
def test_upload_unknown_file_type(
    monkeypatch: pytest.MonkeyPatch,
    client: FlaskClient,
    add_test_objects: AddTestObjects,
    auth: AuthActions,
) -> None:
    """Test uploading of file that's invalid as it can't be determined.

    :param monkeypatch: Mock patch environment and attributes.
    :param client: Test application client.
    :param add_test_objects: Add test objects to test database.
    :param auth: Handle authorization.
    """
    monkeypatch.setattr("app.views.upload.imghdr.what", lambda *_: None)
    user_test_object = UserTestObject(
        ADMIN_USER_USERNAME, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD, admin=True
    )
    add_test_objects.add_test_users(user_test_object)
    auth.login(user_test_object)
    response = client.post(
        UPLOAD_FAVICON, follow_redirects=True, data={FILE: TUX_PNG.open("rb")}
    )
    assert "cannot confirm validity of file" in response.data.decode()


def test_translate_readme(test_app: Flask, runner: FlaskCliRunner) -> None:
    """Test generating of language list.

    :param test_app: Test application.
    :param runner: Test application cli.
    """
    po_files = {
        "es": "# Spanish translations for jss.",
        "de": "# German translations for jss.",
        "fr": "# French translations for jss.",
    }
    expected = """\
# Languages

- French

- German

- Spanish
"""
    for key, value in po_files.items():
        path = test_app.config[TRANSLATIONS_DIR] / key / "LC_MESSAGES"
        path.mkdir(parents=True)
        (path / MESSAGES_PO).write_text(value, encoding="utf-8")
    runner.invoke(args=[TRANSLATE, "readme"], catch_exceptions=False)
    assert (test_app.config[TRANSLATIONS_DIR] / "LANGUAGES.md").read_text(
        encoding="utf-8"
    ) == expected


def test_lexer_readme(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: FlaskCliRunner
) -> None:
    """Test generating of lexer list.

    :param tmp_path: Create and return temporary ``Path`` object.
    :param monkeypatch: Mock patch environment and attributes.
    :param runner: Test application cli.
    """
    content = """\
const hljs = require("highlight.js/lib/core");
const hljsPython = require("highlight.js/lib/languages/python");
const hljsShell = require("highlight.js/lib/languages/shell");
const hljsYaml = require("highlight.js/lib/languages/yaml");

hljs.registerLanguage("python", hljsPython);
hljs.registerLanguage("shell", hljsShell);
hljs.registerLanguage("yaml", hljsYaml);

document.addEventListener("DOMContentLoaded", () => {
  hljs.highlightAll();
});
"""
    expected = """\
# Languages

- python

- shell

- yaml
"""
    # everything after `tmp_path` is the parents that `Path` will
    # traverse from __file__
    #
    # .. code-block: python
    #
    #    ...
    #    root = Path(__file__).parent.parent.parent
    #    ...
    monkeypatch.setattr(
        "app.cli.lexers.Path", lambda _: tmp_path / "app" / "cli" / "lexers.py"
    )
    readme = tmp_path / ".github" / "LEXERS.md"
    highlight_js = tmp_path / "assets" / "js" / "highlight.js"
    readme.parent.mkdir(parents=True)
    highlight_js.parent.mkdir(parents=True)
    highlight_js.write_text(content, encoding="utf-8")
    runner.invoke(args=["lexers", "readme"], catch_exceptions=False)
    assert readme.read_text(encoding="utf-8") == expected
