"""
tests.utils
===========

Utilities for testing.
"""
# pylint: disable=too-few-public-methods,invalid-name
# pylint: disable=too-many-instance-attributes,too-many-arguments
from __future__ import annotations

import typing as t

from click.testing import Result
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash

from app.models import BaseModel, Task, User, db

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
        self, username: str, email: str, password: str, message: str
    ) -> None:
        self.username = username
        self.email = email
        self.password = password
        self.password_hash = generate_password_hash(password)
        self.message = message


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

    def add_test_tasks(self, *task_test_objects: TaskTestObject) -> None:
        """Add task objects to the database.

        :param task_test_objects: Variable number, of any size, of
            ``TaskTestObject`` instances.
        """
        self._add_object(Task, *task_test_objects)


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
