"""
tests.utils
===========

Utilities for testing.
"""
# pylint: disable=too-few-public-methods,disable=invalid-name
# pylint: disable=too-many-instance-attributes
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple

from bs4 import BeautifulSoup
from flask.testing import FlaskClient
from werkzeug import Response
from werkzeug.security import generate_password_hash

UPDATE1 = "/1/update"
ADMIN_USER_USERNAME = "admin"
ADMIN_USER_EMAIL = "admin@test.com"
ADMIN_USER_PASSWORD = "pass0"
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
INVALID_OR_EXPIRED = "invalid or has expired."
MAIL_SERVER = "localhost"
MAIL_USERNAME = MAIN_USER_USERNAME
MAIL_PASSWORD = "unique"
MAIL_PORT = 25


class UserTestObject:
    """Test model attributes.

    :param username:    Username of user object.
    :param email:       Email of user object.
    :param password:    Password, for raw text and comparison hash.
    :param admin:       Is user admin? True or False.
    """

    def __init__(
        self, username: str, email: str, password: str, admin: bool = False
    ) -> None:
        self.username = username
        self.email = email
        self.password = password
        self.password_hash = generate_password_hash(password)
        self.registered_on = MAIN_USER_REGISTERED_ON
        self.admin = admin


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
    request_password_reset_route = f"{prefix}/request_password_reset"

    def __init__(self, client: FlaskClient) -> None:
        self._client = client

    def login(
        self, user_test_object: UserTestObject, follow_redirects: bool = False
    ) -> Response:
        """Set client to the login state.

        :param user_test_object:    Attributes possessed by user.
        :param follow_redirects:    Follow redirects.
        :return:                    Response object.
        """
        return self._client.post(
            self.login_route,
            data={
                "username": user_test_object.username,
                "password": user_test_object.password,
            },
            follow_redirects=follow_redirects,
        )

    def logout(self) -> Response:
        """Set the client to the logout state.

        :return: Response object.
        """
        return self._client.get(self.logout_route)

    def register(
        self, user_test_object: UserTestObject, follow_redirects: bool = False
    ) -> Response:
        """Register a user.

        :param user_test_object:    Attributes possessed by user.
        :param follow_redirects:    Follow redirects.
        :return:                    Response object.
        """
        return self._client.post(
            self.register_route,
            data={
                "username": user_test_object.username,
                "email": user_test_object.email,
                "password": user_test_object.password,
                "confirm_password": user_test_object.password,
            },
            follow_redirects=follow_redirects,
        )

    @staticmethod
    def parse_token_route(html: str) -> str:
        """Parse sent for password resets, verification, etc."""
        return BeautifulSoup(html, features="html.parser").find("a")["href"]

    def follow_token_route(
        self, html: str, follow_redirects: bool = False
    ) -> Response:
        """Follow token sent for password resets, verification, etc.

        :param html:                HTML str object.
        :param follow_redirects:    Follow redirects.
        :return:                    Response object.
        """
        return self._client.get(
            self.parse_token_route(html), follow_redirects=follow_redirects
        )

    def request_password_reset(
        self, email: str, follow_redirects: bool = False
    ) -> Response:
        """Request user password reset.

        :param email:               Email to request reset with.
        :param follow_redirects:    Follow redirects.
        :return:                    Response object.
        """
        return self._client.post(
            self.request_password_reset_route,
            data={"email": email},
            follow_redirects=follow_redirects,
        )


class Recorder:
    """Record  command when invoked."""

    def __init__(self) -> None:
        self.called = False
        self.args: Tuple[Any, ...] = ()
        self.kwargs: Dict[Any, Any] = {}

    def __call__(self, *args: Any, **kwargs: Any) -> Recorder:
        self.called = True
        self.args = args
        self.kwargs = kwargs
        return self
