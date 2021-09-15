"""
tests.conftest
==============

The ``test_app`` fixture will call the factory and pass ``test_config`` to
configure the application and database for testing instead of using
local development configuration.
"""
from pathlib import Path
from typing import Callable

import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from app import create_app
from app.models import Post, User, db

from .utils import AuthActions, PostTestObject, UserTestObject


@pytest.fixture(name="test_app")
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
    return create_app()


@pytest.fixture(name="init_db")
def fixture_init_db(test_app: Flask) -> None:
    """Automatically create a test database for every test instance.

    :param test_app: Test ``Flask`` app object.
    """
    with test_app.app_context():
        db.create_all()


@pytest.fixture(name="add_test_user")
def fixture_add_test_user(test_app: Flask) -> Callable[[UserTestObject], None]:
    """Add a user object to the database.

    :param test_app:    Test ``Flask`` app object.
    :return:            Function for using this fixture.
    """

    def _add_test_user(user_test_object: UserTestObject) -> None:
        with test_app.app_context():
            test_user = User(
                username=user_test_object.username,
                password_hash=user_test_object.password_hash,
                email=user_test_object.email,
            )
            db.session.add(test_user)
            db.session.commit()

    return _add_test_user


@pytest.fixture(name="add_test_post")
def fixture_add_test_post(test_app: Flask) -> Callable[[PostTestObject], None]:
    """Add a post object to the database.

    :param test_app:    Test ``Flask`` app object.
    :return:            Function for using this fixture.
    """

    def _add_test_post(post_test_object: PostTestObject) -> None:
        with test_app.app_context():
            post = Post(
                title=post_test_object.title,
                body=post_test_object.body,
                user_id=post_test_object.user_id,
                created=post_test_object.created,
            )
            db.session.add(post)
            db.session.commit()

    return _add_test_post


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
