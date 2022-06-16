"""
tests.utils
===========

Utilities for testing.
"""
# pylint: disable=too-few-public-methods,invalid-name
# pylint: disable=too-many-instance-attributes,too-many-arguments
from __future__ import annotations

import typing as t
from datetime import datetime

from bs4 import BeautifulSoup
from click.testing import Result
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash
from werkzeug.test import TestResponse

from app.models import BaseModel, Message, Task, User, db

from .const import (
    post_body,
    post_title,
    test_message,
    user_email,
    user_password,
    user_username,
)


class TestObject:
    """Base class for all test objects."""


class UserTestObject(TestObject):
    """Test model attributes.

    :param username: Username of user object.
    :param email: Email of user object.
    :param password: Password, for raw text and comparison hash.
    """

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        message: str,
        confirmed=False,
    ) -> None:
        self.username = username
        self.email = email
        self.password = password
        self.password_hash = generate_password_hash(password)
        self.message = message
        self.confirmed = confirmed


class PostTestObject(TestObject):
    """Test model attributes.

    :param title: Title of the post.
    :param body: Main content of the post.
    """

    def __init__(self, title: str, body: str) -> None:
        self.title = title
        self.body = body


class TaskTestObject(TestObject):
    """Test model attributes.

    :param id: ID of the task.
    :param name: Name of the task.
    :param description: description of the task.
    :param user: User initiating the task.
    """

    def __init__(
        self, id: str, name: str, description: str, user: User
    ) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.user_id = user.id


class MessageTestObject(TestObject):
    """Test model attributes.

    :param sender_id: ID of sender.
    :param recipient_id: ID of recipient.
    :param body: Main content of the post.
    :param created: When the post was created.
    """

    def __init__(
        self, sender_id: int, recipient_id: int, body: str, created: datetime
    ) -> None:
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.body = body
        self.created = created


class AuthActions:
    """Handle all the authentication logic.

    :param client: The ``client`` fixture defined above.
    """

    prefix = "auth"
    register_route = f"{prefix}/register"
    login_route = f"{prefix}/login"
    request_password_reset_route = f"{prefix}/request_password_reset"

    def __init__(self, client: FlaskClient) -> None:
        self._client = client

    def login(
        self, user_test_object: UserTestObject, follow_redirects: bool = False
    ) -> TestResponse:
        """Set client to the login state.

        :param user_test_object: Attributes possessed by user.
        :param follow_redirects: Follow redirects.
        :return: Response object.
        """
        return self._client.post(
            self.login_route,
            data={
                "username": user_test_object.username,
                "password": user_test_object.password,
            },
            follow_redirects=follow_redirects,
        )

    def register(
        self, user_test_object: UserTestObject, follow_redirects: bool = False
    ) -> TestResponse:
        """Register a user.

        :param user_test_object: Attributes possessed by user.
        :param follow_redirects: Follow redirects.
        :return: Response object.
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
        """Parse sent for password resets, verification, etc.

        :param html: HTML to parse.
        :return: href tag parsed from HTML.
        """
        return str(
            BeautifulSoup(html, features="html.parser").find("a")["href"]
        )

    def follow_token_route(
        self, html: str, follow_redirects: bool = False
    ) -> TestResponse:
        """Follow token sent for password resets, verification, etc.

        :param html: HTML str object.
        :param follow_redirects: Follow redirects.
        :return: Response object.
        """
        return self._client.get(
            self.parse_token_route(html), follow_redirects=follow_redirects
        )

    def request_password_reset(
        self, email: str, follow_redirects: bool = False
    ) -> TestResponse:
        """Request user password reset.

        :param email: Email to request reset with.
        :param follow_redirects: Follow redirects.
        :return: Response object.
        """
        return self._client.post(
            self.request_password_reset_route,
            data={"email": email},
            follow_redirects=follow_redirects,
        )

    def logout(self, **kwargs: t.Any) -> TestResponse:
        """Log the current test user out.

        :param kwargs: Kwargs to pass to get.
        :return: Test ``Response`` object.
        """
        return self._client.get(f"/{self.prefix}/logout", **kwargs)


class Recorder:
    """Record  command when invoked."""

    def __init__(self) -> None:
        self.called = False
        self.args: t.Tuple[t.Any, ...] = ()
        self.kwargs: t.Dict[t.Any, t.Any] = {}

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> Recorder:
        self.called = True
        self.args = args
        self.kwargs = kwargs
        return self


class AddTestObjects:
    """Add test objects to test database.

    :param test_app: Test application.
    """

    def __init__(self, test_app: Flask, client: FlaskClient) -> None:
        self.test_app = test_app
        self.test_client = client

    def _add_object(
        self, model: t.Type[BaseModel], *test_objects: TestObject
    ) -> None:
        with self.test_app.app_context():
            for test_object in test_objects:
                instance = model()
                for key, value in vars(test_object).items():
                    setattr(instance, key, value)

                db.session.add(instance)
                db.session.commit()

    def add_test_users(self, *user_test_objects: UserTestObject) -> None:
        """Add user objects to the database.

        :param user_test_objects: Variable number, of any size, of
            ``UserTestObject`` instances.
        """
        self._add_object(User, *user_test_objects)

    def add_test_post(
        self, post_test_object: PostTestObject, **kwargs: t.Any
    ) -> TestResponse:
        """Add post to the database.

        :param post_test_object: ``PostTestObject`` instances.
        :param kwargs: Kwargs to pass to post.
        :return: Test ``Response`` object.
        """
        return self.test_client.post(
            "/post/create",
            data={
                "title": post_test_object.title,
                "body": post_test_object.body,
            },
            **kwargs,
        )

    def add_test_tasks(self, *task_test_objects: TaskTestObject) -> None:
        """Add task objects to the database.

        :param task_test_objects: Variable number, of any size, of
            ``TaskTestObject`` instances.
        """
        self._add_object(Task, *task_test_objects)

    def add_test_messages(
        self, *message_test_objects: MessageTestObject
    ) -> None:
        """Add message objects to the database.

        :param message_test_objects: Variable number, of any size, of
            ``MessageTestObject`` instances.
        """
        self._add_object(Message, *message_test_objects)


class GetObjects:
    """Get test objects with db model attributes."""

    def __init__(self, test_app: Flask) -> None:
        self._test_app = test_app

    @staticmethod
    def post(max_index: int = 0) -> t.List[PostTestObject]:
        """Get a tuple of ``PostTestObject`` instances.

        :param max_index: Maximum number of objects to return by list
            index (0 will return 1 object, 1 will return 2, and so on).
        :return: Tuple of ``PostTestObject`` instances.
        """
        return [
            PostTestObject(post_title[i], post_body[i])
            for i in range(max_index + 1)
        ]

    def user(self, max_index: int = 0) -> t.List[UserTestObject]:
        """Get a tuple of ``UserTestObject`` instances.

        :param max_index: Maximum number of objects to return by list
            index (0 will return 1 object, 1 will return 2, and so on).
        :return: Tuple of ``UserTestObject`` instances.
        """
        return [
            UserTestObject(
                "admin" if i == 0 else user_username[i],
                self._test_app.config["ADMINS"][0]
                if i == 0
                else user_email[i],
                user_password[i],
                test_message[i],
            )
            for i in range(max_index + 1)
        ]


UserFixtureType = t.Callable[[int], None]
ConfirmUserFixtureType = UserFixtureType
AuthorizeUserFixtureType = UserFixtureType
CreateAdminFixtureType = t.Callable[..., Result]
