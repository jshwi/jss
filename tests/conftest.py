"""
tests.conftest
==============

The ``test_app`` fixture will call the factory and pass ``test_config``
to configure the application and database for testing instead of using
local development configuration.
"""
import typing as t
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from app import create_app
from app.models import db

from .const import (
    ADMIN_USER_EMAIL,
    ADMIN_USER_PASSWORD,
    COPYRIGHT_AUTHOR,
    COPYRIGHT_EMAIL,
    INIT_DB,
    LICENSE,
    MAIN_USER_EMAIL,
    TRANSLATIONS_DIR,
)
from .utils import AddTestObjects, AuthActions


@pytest.fixture(name="test_app", autouse=True)
def fixture_test_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Flask:
    """Create an instance of the ``Flask`` app with testing environment.

    The ``DATABASE_URL`` path is overridden, so it points to the test
    path.

    ``TESTING`` tells ``Flask`` that the app is in test mode. ``Flask``
    changes some internal behaviour, so it is easier to test and other
    extensions can also use the flag to make testing them easier.

    :param tmp_path: Create and return temporary directory.
    :param monkeypatch: Mock patch environment and attributes.
    :return: Test application
    """
    monkeypatch.setenv("TESTING", "1")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:////{tmp_path / 'test.db'}")
    monkeypatch.setenv("SECRET_KEY", "testing")
    monkeypatch.setenv("MAIL_SUBJECT_PREFIX", "[JSS]: ")
    monkeypatch.setenv("ADMINS", f"{ADMIN_USER_EMAIL},{MAIN_USER_EMAIL}")
    monkeypatch.setenv("DEFAULT_MAIL_SENDER", "no-reply@test.com")
    monkeypatch.setenv("DEBUG_TB_ENABLED", "0")
    monkeypatch.setenv("ADMIN_SECRET", ADMIN_USER_PASSWORD)
    monkeypatch.setenv(TRANSLATIONS_DIR, str(tmp_path / "translations"))
    monkeypatch.setenv("LICENSE", str(tmp_path / LICENSE))
    monkeypatch.setenv("COPYRIGHT_AUTHOR", COPYRIGHT_AUTHOR)
    monkeypatch.setenv("COPYRIGHT_EMAIL", COPYRIGHT_EMAIL)
    monkeypatch.setenv("SHOW_POSTS", "1")
    return create_app()


@pytest.fixture(name=INIT_DB)
def fixture_init_db(test_app: Flask) -> None:
    """Automatically create a test database for every test instance.

    :param test_app: Test application.
    """
    with test_app.app_context():
        db.create_all()


@pytest.fixture(name="client")
def fixture_client(test_app: Flask) -> FlaskClient:
    """Make requests to the application without running the server.

    :param test_app: Test application.
    :return: Client for testing app.
    """
    return test_app.test_client()


@pytest.fixture(name="runner")
def fixture_runner(test_app: Flask) -> FlaskCliRunner:
    """Creates a runner that can call the registered commands.

    :param test_app: Test application.
    :return: Cli runner for testing app.
    """
    return test_app.test_cli_runner()


@pytest.fixture(name="auth")
def fixture_auth(client: FlaskClient) -> AuthActions:
    """Handle authorization with test app.

    :param client: Test application client.
    :return: Instantiated ``AuthActions`` object - a class acting as a
        wrapper to change the state of the client.
    """
    return AuthActions(client)


@pytest.fixture(name="patch_getpass")
def fixture_patch_getpass(
    monkeypatch: pytest.MonkeyPatch,
) -> t.Callable[[t.List[str]], None]:
    """Patch getpass in the cli module.

    :param monkeypatch: Mock patch environment and attributes.
    :return: Fixture to use this function.
    """

    def _patch_getpass(inputs: t.List[str]) -> None:
        monkeypatch.setattr("app.cli.create.getpass", lambda _: inputs.pop())

    return _patch_getpass


@pytest.fixture(name="interpolate_routes")
def fixture_interpolate_routes() -> t.Callable[..., None]:
    """Interpolate route fields with values for testing.

    :return: Function for using this fixture.
    """

    def _interpolate_routes(
        routes: t.List[str], post_id: int, revision_id, username: str
    ) -> None:
        for count, route in enumerate(routes):
            routes[count] = (
                route.replace("<int:id>", str(post_id))
                .replace("<int:revision>", str(revision_id))
                .replace("<username>", username)
            )

    return _interpolate_routes


@pytest.fixture(name="add_test_objects")
def fixture_add_test_objects(test_app: Flask) -> AddTestObjects:
    """Add test objects to test database.

    :param test_app: Test application.
    :return: Instantiated ``AddTestObjects`` class.
    """
    return AddTestObjects(test_app)


@pytest.fixture(name="init_static")
def fixture_init_static(test_app: Flask, tmp_path: Path) -> None:
    """Initialize static dir and set in app for testing.

    :param test_app: Test application.
    :param tmp_path: Create and return temporary directory.
    """
    # create and set static
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    test_app.static_folder = str(static_dir)

    # add non "built" static files
    setting_files = ["browserconfig.xml"]
    for setting_file in setting_files:
        Path(static_dir / setting_file).touch()

    # create build dir
    build_dir = static_dir / "build"
    build_dir.mkdir()

    # create "built" images
    items = [
        "favicon.ico",
        "mstile-150x150.png",
        "safari-pinned-tab.svg",
        "site.webmanifest",
    ]
    for item in items:
        Path(build_dir / item).touch()
