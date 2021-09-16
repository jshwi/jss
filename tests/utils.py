"""
tests.utils
===========

Utilities for testing.
"""
# pylint: disable=too-few-public-methods,disable=invalid-name
# pylint: disable=too-many-instance-attributes
from datetime import datetime
from typing import Any

from flask.testing import FlaskClient
from werkzeug import Response
from werkzeug.security import generate_password_hash

UPDATE1 = "/1/update"
MAIN_USER_USERNAME = "main"
MAIN_USER_EMAIL = "main@test.com"
MAIN_USER_PASSWORD = "pass1"
OTHER_USER_USERNAME = "other"
OTHER_USER_EMAIL = "other@test.com"
OTHER_USER_PASSWORD = "pass2"
POST_TITLE = "test title"
POST_BODY = "test\nbody"
POST_AUTHOR_ID = 1
POST_CREATED = datetime(2018, 1, 1, 0, 0, 0)
MAIN_USER_REGISTERED_ON = datetime(2018, 1, 1, 0, 0, 1)


class UserTestObject:
    """Test model attributes.

    :param username:    Username of user object.
    :param email:       Email of user object.
    :param password:    Password, for raw text and comparison hash.
    """

    def __init__(self, username: str, email: str, password: str) -> None:
        self.username = username
        self.email = email
        self.password = password
        self.password_hash = generate_password_hash(password)
        self.registered_on = MAIN_USER_REGISTERED_ON


class PostTestObject:
    """Test model attributes.

    :param title:       Title of the post.
    :param body:        Main content of the post..
    :param user_id:   ID of the user who made the post.
    :param created:     When the post was created.
    """

    def __init__(
        self, title: str, body: str, user_id: int, created: datetime
    ) -> None:
        self.title = title
        self.body = body
        self.user_id = user_id
        self.created = created


class AuthActions:
    """Handle all the authentication logic.

    :param client: The ``client`` fixture defined above.
    """

    prefix = "auth"
    register_route = f"{prefix}/register"
    login_route = f"{prefix}/login"
    logout_route = f"{prefix}/logout"

    def __init__(self, client: FlaskClient) -> None:
        self._client = client

    def login(self, user_test_object: UserTestObject) -> Response:
        """Set client to the login state.

        :param user_test_object:    Attributes possessed by user.
        :return:                    Response object.
        """
        return self._client.post(
            self.login_route,
            data={
                "username": user_test_object.username,
                "password": user_test_object.password,
            },
        )

    def logout(self) -> Response:
        """Set the client to the logout state.

        :return: Response object.
        """
        return self._client.get(self.logout_route)

    def register(self, user_test_object: UserTestObject) -> Response:
        """Register a user.

        :param user_test_object:    Attributes possessed by user.
        :return:                    Response object.
        """
        return self._client.post(
            self.register_route,
            data={
                "username": user_test_object.username,
                "email": user_test_object.email,
                "password": user_test_object.password,
            },
        )


class Recorder:
    """Record  command when invoked."""

    def __init__(self) -> None:
        self.called = False

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.called = True
