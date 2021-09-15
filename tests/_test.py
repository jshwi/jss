"""
tests._test
===========
"""
# pylint: disable=too-many-arguments,too-many-lines
import json
from typing import Callable, List

import pytest
from flask import Flask, g, session
from flask.testing import FlaskClient, FlaskCliRunner

from app.extensions import mail
from app.mail import send_email
from app.models import Post, User, db

from .utils import (
    ADMIN_USER_PASSWORD,
    MAIN_USER_EMAIL,
    MAIN_USER_PASSWORD,
    MAIN_USER_USERNAME,
    OTHER_USER_EMAIL,
    OTHER_USER_PASSWORD,
    OTHER_USER_USERNAME,
    POST_AUTHOR_ID,
    POST_BODY,
    POST_CREATED,
    POST_TITLE,
    UPDATE1,
    AuthActions,
    PostTestObject,
    Recorder,
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

    :param test_app:    Test ``Flask`` app object.
    :param client:      App's test-client API.
    :param auth:        Handle authorization with test app.
    """
    assert client.get("/auth/register").status_code == 200
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    response = auth.register(user_test_object)
    assert response.headers["Location"] == "http://localhost/auth/login"
    with test_app.app_context():
        user = User.query.filter_by(username=user_test_object.username).first()
        assert user is not None


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize(
    "username,email,password,message",
    [
        ("", "", "", b"Username is required."),
        (OTHER_USER_USERNAME, "", "", b"Email is required."),
        ("a", OTHER_USER_EMAIL, "", b"Password is required."),
        (
            MAIN_USER_USERNAME,
            OTHER_USER_EMAIL,
            MAIN_USER_PASSWORD,
            b"already registered",
        ),
        (
            OTHER_USER_USERNAME,
            MAIN_USER_EMAIL,
            MAIN_USER_PASSWORD,
            b"already registered",
        ),
    ],
    ids=[
        "no-username",
        "no-email",
        "no-password",
        "name-taken",
        "email-taken",
    ],
)
def test_register_validate_input(
    auth: AuthActions,
    add_test_user: Callable[[UserTestObject], None],
    username: str,
    email: str,
    password: str,
    message: str,
) -> None:
    """Test invalid input and error messages.

    :param auth:            Handle authorization with test app.
    :param add_test_user:   Add user to test database.
    :param username:        The test username input.
    :param password:        The test password input.
    :param message:         The expected message for the response.
    """
    registered = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    registering = UserTestObject(username, email, password)
    add_test_user(registered)
    response = auth.register(registering)
    assert message in response.data


@pytest.mark.usefixtures("init_db")
def test_login(
    client: FlaskClient,
    auth: AuthActions,
    add_test_user: Callable[[UserTestObject], None],
) -> None:
    """Test login functionality.

    :param client:          Flask client testing helper.
    :param auth:            Handle authorization with test app.
    :param add_test_user:   Add user to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_user(user_test_object)
    response = auth.login(user_test_object)
    assert response.headers["Location"] == "http://localhost/"
    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user.username == user_test_object.username


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize(
    "username,password",
    [
        ("not-a-username", MAIN_USER_PASSWORD),
        (MAIN_USER_USERNAME, "not-a-password"),
    ],
    ids=["incorrect-username", "incorrect-password"],
)
def test_login_validate_input(
    auth: AuthActions,
    add_test_user: Callable[[UserTestObject], None],
    username: str,
    password: str,
) -> None:
    """Test incorrect username and password error messages.

    :param auth:            Handle authorization with test app.
    :param add_test_user:   Add user to test database.
    :param username:        Parametrized incorrect username
    :param password:        Parametrized incorrect password
    """
    registered_user = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_user(registered_user)
    test_user = UserTestObject(username, OTHER_USER_EMAIL, password)
    response = auth.login(test_user)
    assert b"Invalid username or password" in response.data


@pytest.mark.usefixtures("init_db")
def test_logout(client: FlaskClient, auth: AuthActions) -> None:
    """Test logout functionality.

    :param client:  Client for testing app.
    :param auth:    Handle authorization with test app.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    auth.login(user_test_object)
    with client:
        auth.logout()
        assert "user_id" not in session


@pytest.mark.usefixtures("init_db")
def test_index(
    client: FlaskClient,
    auth: AuthActions,
    add_test_user: Callable[[UserTestObject], None],
    add_test_post: Callable[[PostTestObject], None],
) -> None:
    """Test login and subsequent requests from the client.

    The index view should display information about the post that was
    added with the test data. When logged in as the author there should
    be a link to edit the post.

    We can also test some more authentication behaviour while testing
    the index view. When not logged in each pages shows links to log in
    or register. When logged in there's a link to log out.

    :param client:          Client for testing app.
    :param auth:            Handle authorization with test app.
    :param add_test_user:   Add user to test database.
    :param add_test_post:   Add post to test database.
    """
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    post_test_object = PostTestObject(
        POST_TITLE, POST_BODY, POST_AUTHOR_ID, POST_CREATED
    )
    add_test_user(user_test_object)
    add_test_post(post_test_object)
    auth.login(user_test_object)
    response = client.get("/").data.decode()
    assert "Log Out" in response
    assert post_test_object.title in response
    assert f"by {user_test_object.username}" in response
    assert str(post_test_object.created).split()[0] in response
    assert post_test_object.body in response
    assert 'href="/1/update"' in response


@pytest.mark.parametrize("route", ["/create", UPDATE1, "/1/delete"])
def test_login_required(client: FlaskClient, route: str) -> None:
    """Test requirement that user be logged in to post.

    A user must be logged in to access the create, update, and delete
    views.

    The logged in user must be the author of the post to access the
    update and delete views, otherwise a ``403 Forbidden`` status is
    returned.

    :param client:  Client for testing app.
    :param route:   Parametrized route path.
    """
    response = client.post(route)
    assert response.headers["Location"] == "http://localhost/auth/login"


@pytest.mark.usefixtures("init_db")
def test_author_required(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_user: Callable[[UserTestObject], None],
    add_test_post: Callable[[PostTestObject], None],
) -> None:
    """Test author's name when required.

    The create and update views should render and return a ``200 OK``
    status for a ``GET`` request.

    When valid data is sent in a ``POST`` request the create view should
    insert the new post data into the database and the update view
    should modify the existing data. Both pages should show an error
    message on invalid data.

    :param test_app:        Test ``Flask`` app object.
    :param client:          Client for testing app.
    :param auth:            Handle authorization with test app.
    :param add_test_user:   Add user to test database.
    :param add_test_post:   Add post to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    other_user_test_object = UserTestObject(
        OTHER_USER_USERNAME, OTHER_USER_EMAIL, OTHER_USER_PASSWORD
    )
    add_test_user(user_test_object)
    add_test_user(other_user_test_object)
    post_test_object = PostTestObject(
        POST_TITLE, POST_BODY, POST_AUTHOR_ID, POST_CREATED
    )
    add_test_post(post_test_object)
    # change the post author to another author
    with test_app.app_context():
        post = Post.query.get(1)
        post.user_id = 2
        db.session.commit()

    auth.login(user_test_object)
    # current user cannot modify other user's post
    assert client.post(UPDATE1).status_code == 403
    assert client.post("/1/delete").status_code == 403

    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize("route", ["/2/update", "/2/delete"])
def test_exists_required(
    client: FlaskClient,
    auth: AuthActions,
    route: str,
    add_test_user: Callable[[UserTestObject], None],
    add_test_post: Callable[[PostTestObject], None],
) -> None:
    """Test ``404 Not Found`` is returned when a route does not exist.

    :param client:          Client for testing app.
    :param auth:            Handle authorization with test app.
    :param route:           Parametrized route path.
    :param add_test_user:   Add user to test database.
    :param add_test_post:   Add post to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    post_test_object = PostTestObject(
        POST_TITLE, POST_BODY, POST_AUTHOR_ID, POST_CREATED
    )
    add_test_user(user_test_object)
    add_test_post(post_test_object)
    auth.login(user_test_object)
    response = client.post(route)
    assert response.status_code == 404


@pytest.mark.usefixtures("init_db")
def test_create(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_user: Callable[[UserTestObject], None],
) -> None:
    """Test create view functionality.

    When valid data is sent in a ``POST`` request the create view should
    insert the new post data into the database.

    :param test_app:        Test ``Flask`` app object.
    :param client:          Client for testing app.
    :param auth:            Handle authorization with test app.
    :param add_test_user:   Add user to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_user(user_test_object)
    auth.login(user_test_object)
    assert client.get("/create").status_code == 200
    client.post("/create", data={"title": POST_TITLE, "body": POST_BODY})
    with test_app.app_context():
        count = Post.query.count()
        assert count == 1


@pytest.mark.usefixtures("init_db")
def test_update(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_user: Callable[[UserTestObject], None],
    add_test_post: Callable[[PostTestObject], None],
) -> None:
    """Test update view modifies the existing data.

    :param test_app:        Test ``Flask`` app object.
    :param client:          Client for testing app.
    :param auth:            Handle authorization with test app.
    :param add_test_user:   Add user to test database.
    :param add_test_post:   Add post to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    created_post = PostTestObject(
        POST_TITLE, POST_BODY, POST_AUTHOR_ID, POST_CREATED
    )
    updated_post = PostTestObject(
        "updated title", "updated body", POST_AUTHOR_ID, POST_CREATED
    )
    add_test_user(user_test_object)
    add_test_post(created_post)
    auth.login(user_test_object)
    assert client.get(UPDATE1).status_code == 200
    client.post(
        UPDATE1, data={"title": updated_post.title, "body": updated_post.body}
    )
    with test_app.app_context():
        post = Post.query.get(1)
        assert post.title == updated_post.title
        assert post.body == updated_post.body


@pytest.mark.usefixtures("init_db")
@pytest.mark.parametrize("route", ["/create", UPDATE1])
def test_create_update_validate(
    client: FlaskClient,
    auth: AuthActions,
    add_test_user: Callable[[UserTestObject], None],
    add_test_post: Callable[[PostTestObject], None],
    route: str,
) -> None:
    """Both pages should show an error message on invalid data.

    :param client:          Client for testing app.
    :param auth:            Handle authorization with test app.
    :param add_test_user:   Add user to test database.
    :param add_test_post:   Add post to test database.
    :param route:           Parametrized route path.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_user(user_test_object)
    post_test_object = PostTestObject(
        POST_TITLE, POST_BODY, POST_AUTHOR_ID, POST_CREATED
    )
    add_test_post(post_test_object)
    auth.login(user_test_object)
    other_post = PostTestObject("", "", POST_AUTHOR_ID, POST_CREATED)
    response = client.post(
        route,
        data={"title": other_post.title, "body": other_post.body},
        follow_redirects=True,
    )
    assert b"Title is required" in response.data


@pytest.mark.usefixtures("init_db")
def test_delete(
    test_app: Flask,
    client: FlaskClient,
    auth: AuthActions,
    add_test_user: Callable[[UserTestObject], None],
    add_test_post: Callable[[PostTestObject], None],
) -> None:
    """Test deletion of posts.

    The delete view should redirect to the index URl and the post should
    no longer exist in the database.

    :param test_app:        Test ``Flask`` app object.
    :param client:          Client for testing app.
    :param auth:            Handle authorization with test app.
    :param add_test_user:   Add user to test database.
    :param add_test_post:   Add post to test database.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_user(user_test_object)
    post_test_object = PostTestObject(
        POST_TITLE, POST_BODY, POST_AUTHOR_ID, POST_CREATED
    )
    add_test_post(post_test_object)
    auth.login(user_test_object)
    response = client.post("/1/delete")
    assert response.headers["Location"] == "http://localhost/"
    with test_app.app_context():
        post = Post.query.get(1)
        assert post is None


def test_create_command(
    runner: FlaskCliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test cli.

    :param runner:          Fixture derived from the ``create_app``
                            factory fixture used to call the ``init-db``
                            command by name.
    :param monkeypatch:     Mock patch environment and attributes.
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
    post = Post(title=POST_TITLE, body=POST_BODY, created=POST_CREATED)
    as_dict = post.export()
    assert as_dict["title"] == POST_TITLE
    assert as_dict["body"] == POST_BODY
    assert as_dict["created"] == str(POST_CREATED)


@pytest.mark.parametrize("sync", [True, False])
def test_send_mail(test_app: Flask, sync: bool) -> None:
    """Test sending of mail by app's email client.

    :param test_app:    Test ``Flask`` app object.
    :param sync:        Asynchronous: True or False.
    """
    subject = "mail subject line"
    recipients = [MAIN_USER_EMAIL, OTHER_USER_EMAIL]
    html = "<p>email body<p>"
    sender = "admin@localhost"
    data = {
        "title": POST_TITLE,
        "body": POST_BODY,
        "created": f"{POST_CREATED.isoformat()}Z",
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
    patch_getpass: Callable[[List[str]], None],
) -> None:
    """Test creation of a new user that doesn't exist.

    :param test_app:        Test ``Flask`` app object.
    :param runner:          Fixture derived from the ``create_app``
                            factory fixture used to call the ``init-db``
                            command by name.
    :param patch_getpass:   Patch getpass to receive list of passwords.
    """
    patch_getpass([MAIN_USER_PASSWORD, MAIN_USER_PASSWORD])
    user_input = f"{MAIN_USER_USERNAME}\n{MAIN_USER_EMAIL}"
    response = runner.invoke(args=["create", "user"], input=user_input)
    assert "user successfully created" in response.output
    with test_app.app_context():
        user = User.query.filter_by(username=MAIN_USER_USERNAME).first()
        assert user.check_password(MAIN_USER_PASSWORD)


@pytest.mark.usefixtures("init_db")
def test_create_user_exists(
    runner: FlaskCliRunner, add_test_user: Callable[[UserTestObject], None]
) -> None:
    """Test creation of a new user that exists.

    :param runner:  Fixture derived from the ``create_app`` factory
                    fixture used to call the ``init-db`` command by
                    name.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    add_test_user(user_test_object)
    response = runner.invoke(args=["create", "user"], input=MAIN_USER_USERNAME)
    assert "username is taken" in response.output


@pytest.mark.usefixtures("init_db")
def test_create_user_email_exists(
    runner: FlaskCliRunner, add_test_user: Callable[[UserTestObject], None]
) -> None:
    """Test creation of a new user who's email is already registered.

    :param runner:  Fixture derived from the ``create_app`` factory
                    fixture used to call the ``init-db`` command by
                    name.
    """
    user_test_object = UserTestObject(
        MAIN_USER_USERNAME, MAIN_USER_EMAIL, MAIN_USER_PASSWORD
    )
    user_input = f"{OTHER_USER_EMAIL}\n{MAIN_USER_EMAIL}"
    add_test_user(user_test_object)
    response = runner.invoke(args=["create", "user"], input=user_input)
    assert (
        "a user with this email address is already registered"
        in response.output
    )


@pytest.mark.usefixtures("init_db")
def test_create_user_passwords_no_match(
    runner: FlaskCliRunner, patch_getpass: Callable[[List[str]], None]
) -> None:
    """Test creation of a new user where passwords don't match.

    :param runner:  Fixture derived from the ``create_app`` factory
                    fixture used to call the ``init-db`` command by
                    name.
    """
    patch_getpass([MAIN_USER_PASSWORD, OTHER_USER_PASSWORD])
    user_input = f"{MAIN_USER_USERNAME}\n{MAIN_USER_EMAIL}"
    response = runner.invoke(args=["create", "user"], input=user_input)
    assert "passwords do not match: could not add user" in response.output


@pytest.mark.usefixtures("init_db")
def test_create_admin(
    monkeypatch: pytest.MonkeyPatch, test_app: Flask, runner: FlaskCliRunner
) -> None:
    """Test commands called when invoking ``flask create admin``.

    :param monkeypatch:     Mock patch environment and attributes.
    :param test_app:        Test ``Flask`` app object.
    :param runner:          Fixture derived from the ``create_app``
                            factory fixture used to call the command by
                            name.
    """
    monkeypatch.setenv("ADMIN_SECRET", ADMIN_USER_PASSWORD)
    response = runner.invoke(args=["create", "admin"])
    assert "admin successfully created" in response.output
    with test_app.app_context():
        admin = User.query.filter_by(username="admin").first()
        assert admin.email == test_app.config["ADMINS"][0]
        assert admin.check_password(ADMIN_USER_PASSWORD)
