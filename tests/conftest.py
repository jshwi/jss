"""
tests.conftest
==============

The ``test_app`` fixture will call the factory and pass ``test_config`` to
configure the application and database for testing instead of using
local development configuration.
"""
from pathlib import Path
from typing import Callable, List

import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from app import create_app
from app.models import Post, Task, User, db

from .utils import (
    ADMIN_USER_EMAIL,
    MAIN_USER_EMAIL,
    AuthActions,
    PostTestObject,
    TaskTestObject,
    UserTestObject,
)


@pytest.fixture(name="test_app", autouse=True)
def fixture_test_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Flask:
    """Create an instance of the ``Flask`` app with testing environment.

    The ``DATABASE_URL`` path is overridden so it points to the test
    path.

    ``TESTING`` tells ``Flask`` that the app is in test mode. ``Flask``
    changes some internal behaviour so it is easier to test and other
    extensions can also use the flag to make testing them easier.

    :param tmp_path:    Create and return temporary directory.
    :param monkeypatch: Mock patch environment and attributes.
    :param:             Test ``Flask`` app object.
    """
    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:////{tmp_path / 'test.db'}")
    monkeypatch.setenv("SECRET_KEY", "testing")
    monkeypatch.setenv("MAIL_SUBJECT_PREFIX", "[JSS]: ")
    monkeypatch.setenv("ADMINS", f"{ADMIN_USER_EMAIL},{MAIN_USER_EMAIL}")
    monkeypatch.setenv("DEFAULT_MAIL_SENDER", "no-reply@test.com")
    return create_app()


@pytest.fixture(name="init_db")
def fixture_init_db(test_app: Flask) -> None:
    """Automatically create a test database for every test instance.

    :param test_app: Test ``Flask`` app object.
    """
    with test_app.app_context():
        db.create_all()


@pytest.fixture(name="add_test_user")
def fixture_add_test_user(test_app: Flask) -> Callable[..., None]:
    """Add a user object to the database.

    :param test_app:    Test ``Flask`` app object.
    :return:            Function for using this fixture.
    """

    # noinspection PyArgumentList
    def _add_test_user(*user_test_objects: UserTestObject) -> None:
        with test_app.app_context():
            for user_test_object in user_test_objects:
                test_user = User(
                    username=user_test_object.username,
                    password_hash=user_test_object.password_hash,
                    email=user_test_object.email,
                    admin=user_test_object.admin,
                    confirmed=user_test_object.confirmed,
                )
                db.session.add(test_user)
                db.session.commit()

    return _add_test_user


@pytest.fixture(name="add_test_post")
def fixture_add_test_post(test_app: Flask) -> Callable[..., None]:
    """Add a post object to the database.

    :param test_app:    Test ``Flask`` app object.
    :return:            Function for using this fixture.
    """

    def _add_test_post(*post_test_objects: PostTestObject) -> None:
        with test_app.app_context():
            for post_test_object in post_test_objects:
                post = Post(
                    title=post_test_object.title,
                    body=post_test_object.body,
                    user_id=post_test_object.user_id,
                    created=post_test_object.created,
                )
                db.session.add(post)
                db.session.commit()

    return _add_test_post


@pytest.fixture(name="add_test_task")
def fixture_add_test_task(test_app: Flask) -> Callable[..., None]:
    """Add a task object to the database.

    :param test_app:    Test ``Flask`` app object.
    :return:            Function for using this fixture.
    """

    def _add_test_task(*task_test_objects: TaskTestObject) -> None:
        with test_app.app_context():
            for post_test_object in task_test_objects:
                task = Task(
                    id=post_test_object.id,
                    name=post_test_object.name,
                    description=post_test_object.description,
                    user_id=post_test_object.user_id,
                )
                db.session.add(task)
                db.session.commit()

    return _add_test_task


@pytest.fixture(name="client")
def fixture_client(test_app: Flask) -> FlaskClient:
    """Make requests to the application without running the server.

    :param test_app:    Test ``Flask`` app object.
    :return:            Client for testing app.
    """
    return test_app.test_client()


@pytest.fixture(name="runner")
def fixture_runner(test_app: Flask) -> FlaskCliRunner:
    """Creates a runner that can call the registered commands.

    :param test_app:    Test ``Flask`` app object.
    :return:            Cli runner for testing app.
    """
    return test_app.test_cli_runner()


@pytest.fixture(name="auth")
def fixture_auth(client: FlaskClient) -> AuthActions:
    """Handle authorization with test app.

    :param client:  Client for testing app.
    :return:        Instantiated ``AuthActions`` object - a class acting
                    as a wrapper to change the state of the client.
    """
    return AuthActions(client)


@pytest.fixture(name="patch_getpass")
def fixture_patch_getpass(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[List[str]], None]:
    """Patch getpass in the cli module.

    :param monkeypatch: Mock patch environment and attributes.
    :return:            Fixture to use this function.
    """

    def _patch_getpass(inputs: List[str]) -> None:
        monkeypatch.setattr("app.user.getpass", lambda _: inputs.pop())

    return _patch_getpass
