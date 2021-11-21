"""
tests.utils
===========

Utilities for testing.
"""
# pylint: disable=too-few-public-methods,invalid-name
# pylint: disable=too-many-instance-attributes,too-many-arguments
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple, Type

from bs4 import BeautifulSoup
from flask import Flask
from flask.testing import FlaskClient
from werkzeug import Response
from werkzeug.security import generate_password_hash

from app.utils.models import BaseModel, Message, Post, Task, User, db

UPDATE1 = "/post/1/update"
ADMIN_USER_USERNAME = "admin"
ADMIN_USER_EMAIL = "admin@test.com"
ADMIN_USER_PASSWORD = "pass0"
AUTHORIZED_USER_USERNAME = "authorized"
AUTHORIZED_USER_EMAIL = "authorized@test.com"
AUTHORIZED_USER_PASSWORD = "pass1"
MAIN_USER_USERNAME = "main"
MAIN_USER_EMAIL = "main@test.com"
MAIN_USER_PASSWORD = "pass2"
OTHER_USER_USERNAME = "other"
OTHER_USER_EMAIL = "other@test.com"
OTHER_USER_PASSWORD = "pass3"
LAST_USER_USERNAME = "last"
LAST_USER_EMAIL = "last@test.com"
LAST_USER_PASSWORD = "pass4"
POST_TITLE_1 = "test title 1"
POST_BODY_1 = "test 1\nbody 1"
POST_AUTHOR_ID_1 = 1
POST_TITLE_2 = "test title 2"
POST_BODY_2 = "test 2\nbody 2"
POST_AUTHOR_ID_2 = 2
POST_TITLE_3 = "test title 3"
POST_BODY_3 = "test 3\nbody 3"
POST_AUTHOR_ID_3 = 3
POST_TITLE_4 = "test title 4"
POST_BODY_4 = "test 4\nbody 4"
POST_AUTHOR_ID_4 = 4
POST_TITLE_V1 = "title-v1"
POST_TITLE_V2 = "body-v1"
POST_BODY_V1 = "title-v2"
POST_BODY_V2 = "body-v2"
POST_TITLE_V3 = "title-v3"
POST_BODY_V3 = "body-v3"
POST_CREATED_1 = datetime(2018, 1, 1, 0, 0, 1)
POST_CREATED_2 = datetime(2018, 1, 1, 0, 0, 2)
POST_CREATED_3 = datetime(2018, 1, 1, 0, 0, 3)
POST_CREATED_4 = datetime(2018, 1, 1, 0, 0, 4)
MESSAGE_CREATED = datetime(2018, 1, 1, 0, 0, 5)
INVALID_OR_EXPIRED = "invalid or has expired."
MAIL_SERVER = "localhost"
MAIL_USERNAME = MAIN_USER_USERNAME
MAIL_PASSWORD = "unique"
MAIL_PORT = 25
PROFILE_EDIT = "/user/profile/edit"
TASK_ID = "123"
TASK_NAME = "export_posts"
TASK_DESCRIPTION = "Exporting posts..."
MISC_PROGRESS_INT = 37
APP_MODELS_JOB_FETCH = "app.utils.models.Job.fetch"
ADMIN_ROUTE = "/admin"
ADMIN_USER_ROUTE = "/admin/users"
COPYRIGHT_YEAR = "2021"
COPYRIGHT_AUTHOR = "John Doe"
COPYRIGHT_EMAIL = "john.doe@test.com"
RECIPIENT_ID = 1
SENDER_ID = 2
MESSAGE_BODY = "hello, this is a test message"
LICENSE = f"""\
MIT License

Copyright (c) {COPYRIGHT_YEAR} {COPYRIGHT_AUTHOR}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
SETUP_FILE = f"""\
from setuptools import setup, find_packages

with open("README.rst") as file:
    README = file.read()


setup(
    name="package",
    version="0.1.0",
    description="A package",
    long_description=README,
    long_description_content_type="text/x-rst",
    author="John Doe",
    author_email="{COPYRIGHT_EMAIL}",
    url="https://github.com/does_not/exist",
    license="MIT",
    platforms="GNU/Linux",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    keywords=["python3.8"],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask==2.0.2"],
    python_requires=">=3.8",
)
"""
STATUS_CODE_TO_ROUTE_DEFAULT = [
    (
        200,  # all OK
        [
            "/",
            "/auth/login",
            "/auth/register",
            "/auth/request_password_reset",
            "/post/<int:id>",
            "/profile/<username>",
            "/auth/logout",
            "/auth/reset_password/<token>",
            "/favicon.ico",
            "/android-chrome-192x192.png",
            "/android-chrome-512x512.png",
            "/apple-touch-icon.png",
            "/favicon-16x16.png",
            "/favicon-32x32.png",
            "/mstile-150x150.png",
            "/safari-pinned-tab.svg",
            "/site.webmanifest",
        ],
    ),
    (
        401,  # unauthorized,
        [
            "/admin/",
            "/redirect/<token>",
            "/redirect/resend",
            "/auth/unconfirmed",
            "/post/create",
            "/redirect/export_posts",
            "/user/messages",
            "/user/profile/edit",
            "/user/send_message/<recipient>",
            "/user/messages",
            "/user/notifications",
            "/post/<int:id>/update",
        ],
    ),
    (
        405,  # method not allowed
        [
            "/redirect/follow/<username>",
            "/redirect/unfollow/<username>",
            "/redirect/<int:id>/delete",
            "/report/csp_violations",
        ],
    ),
]
COVERED_ROUTES = [r for _, l in STATUS_CODE_TO_ROUTE_DEFAULT for r in l]


class TestObject:
    """Base class for all test objects."""


class UserTestObject(TestObject):
    """Test model attributes.

    :param username: Username of user object.
    :param email: Email of user object.
    :param password: Password, for raw text and comparison hash.
    :param admin: Is user admin? True or False.
    :param authorized: Is user authorized? True or False.
    """

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        admin: bool = False,
        authorized=False,
        confirmed=False,
    ) -> None:
        self.username = username
        self.email = email
        self.password = password
        self.password_hash = generate_password_hash(password)
        self.admin = admin
        self.authorized = authorized
        self.confirmed = confirmed


class PostTestObject(TestObject):
    """Test model attributes.

    :param title: Title of the post.
    :param body: Main content of the post..
    :param user_id: ID of the user who made the post.
    :param created: When the post was created.
    """

    def __init__(
        self, title: str, body: str, user_id: int, created: datetime
    ) -> None:
        self.title = title
        self.body = body
        self.user_id = user_id
        self.created = created


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
    :param body: Main content of the post..
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
    ) -> Response:
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
    ) -> Response:
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
        """Parse sent for password resets, verification, etc."""
        return BeautifulSoup(html, features="html.parser").find("a")["href"]

    def follow_token_route(
        self, html: str, follow_redirects: bool = False
    ) -> Response:
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
    ) -> Response:
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


class AddTestObjects:
    """Add test objects to test database.

    :param test_app: Test ``Flask`` app object.
    """

    def __init__(self, test_app: Flask) -> None:
        self.test_app = test_app

    def _add_object(
        self, model: Type[BaseModel], *test_objects: TestObject
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

    def add_test_posts(self, *post_test_objects: PostTestObject) -> None:
        """Add post objects to the database.

        :param post_test_objects: Variable number, of any size, of
            ``PostTestObject`` instances.
        """
        self._add_object(Post, *post_test_objects)

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
