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
from flask import Flask
from flask.testing import FlaskClient
from werkzeug import Response
from werkzeug.security import generate_password_hash

from app.models import BaseModel, Message, Post, Task, User, db

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
APP_MODELS_JOB_FETCH = "app.models.Job.fetch"
ADMIN_ROUTE = "/admin"
ADMIN_USER_ROUTE = "/admin/users"
COPYRIGHT_YEAR = "2021"
COPYRIGHT_AUTHOR = "John Doe"
COPYRIGHT_EMAIL = "john.doe@test.com"
RECIPIENT_ID = 1
SENDER_ID = 2
MESSAGE_BODY = "hello, this is a test message"
REDIRECT_LOGOUT = "/redirect/logout"
POST_1 = "/post/1"
APP_UTILS_LANG_POT_FILE = "app.utils.lang._pot_file"
APP_UTILS_LANG_SUBPROCESS_RUN = "app.utils.lang.subprocess.run"
MESSAGES_POT = "messages.pot"
MESSAGES_PO = "messages.po"
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
PYPROJECT_TOML = f"""\
[tool.poetry]
authors = [
    "jshwi <{COPYRIGHT_EMAIL}>",
]
description = "A Flask webapp"
keywords = [
    "flask",
    "webapp",
    "pwa",
    "jshwisolutions",
    "blog",
]
license = "MIT"
name = "jss"
packages = [{{ include = "app" }}]
readme = "README.rst"
version = "1.16.2"
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
    :param body: Main content of the post.
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
        self.args: t.Tuple[t.Any, ...] = ()
        self.kwargs: t.Dict[t.Any, t.Any] = {}

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> Recorder:
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


POT_CONTENTS = """
# Translations template for PROJECT.
# Copyright (C) 2022 ORGANIZATION
# This file is distributed under the same license as the PROJECT project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2022.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: PROJECT VERSION\\n"
"Report-Msgid-Bugs-To: EMAIL@ADDRESS\\n"
"POT-Creation-Date: 2022-06-02 14:34+1000\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=utf-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: Babel 2.10.1\\n"

#: app/forms.py:34 app/forms.py:75
msgid "Username"
msgstr ""

#: app/forms.py:37 app/forms.py:94
msgid "Email"
msgstr ""

#: app/forms.py:39 app/forms.py:76 app/forms.py:101
msgid "Password"
msgstr ""

#: app/forms.py:41 app/forms.py:103
msgid "Confirm Password"
msgstr ""

#: app/dom/navbar.py:90 app/forms.py:44 app/templates/auth/register.html:6
msgid "Register"
msgstr ""

#: app/forms.py:56
msgid "Username is taken"
msgstr ""

#: app/forms.py:68
msgid "A user with this email address is already registered"
msgstr ""

#: app/forms.py:77
msgid "Remember Me"
msgstr ""

#: app/forms.py:78 app/templates/auth/login.html:6
msgid "Sign In"
msgstr ""

#: app/forms.py:84
msgid "Title"
msgstr ""

#: app/forms.py:86
msgid "Body"
msgstr ""

#: app/forms.py:88 app/forms.py:116 app/forms.py:122 app/forms.py:131
msgid "Submit"
msgstr ""

#: app/forms.py:95
msgid "Request Password Reset"
msgstr ""

#: app/forms.py:104
msgid "password"
msgstr ""

#: app/forms.py:106 app/templates/auth/reset_password.html:6
msgid "Reset Password"
msgstr ""

#: app/forms.py:112
msgid "username"
msgstr ""

#: app/forms.py:114
msgid "About me"
msgstr ""

#: app/forms.py:129
msgid "Message"
msgstr ""

#: app/dom/macros.py:51
msgid "Versions"
msgstr ""

#: app/dom/macros.py:131
msgid "Previous"
msgstr ""

#: app/dom/macros.py:142
msgid "Next"
msgstr ""

#: app/dom/navbar.py:25 app/templates/user/messages.html:7
msgid "Messages"
msgstr ""

#: app/dom/navbar.py:42
msgid "Profile"
msgstr ""

#: app/dom/navbar.py:44
msgid "Logout"
msgstr ""

#: app/dom/navbar.py:48
msgid "Console"
msgstr ""

#: app/dom/navbar.py:49
msgid "RQ Dashboard"
msgstr ""

#: app/dom/navbar.py:68
msgid "Home"
msgstr ""

#: app/dom/navbar.py:76
msgid "New"
msgstr ""

#: app/dom/navbar.py:91
msgid "Login"
msgstr ""

#: app/routes/redirect.py:44
msgid "Account already confirmed. Please login."
msgstr ""

#: app/routes/redirect.py:50
msgid "Your account has been verified."
msgstr ""

#: app/routes/redirect.py:53
msgid "The confirmation link is invalid or has expired."
msgstr ""

#: app/routes/redirect.py:80
msgid "A new confirmation email has been sent."
msgstr ""

#: app/routes/redirect.py:121
#, python-format
msgid "You are now following %(username)s"
msgstr ""

#: app/routes/redirect.py:144
#, python-format
msgid "You are no longer following %(username)s"
msgstr ""

#: app/routes/redirect.py:162
msgid "An export task is already in progress"
msgstr ""

#: app/templates/posts.html:23 app/templates/public/profile.html:35
msgid "Edit"
msgstr ""

#: app/templates/auth/login.html:16
msgid "New User?"
msgstr ""

#: app/templates/auth/login.html:16
msgid "Click to Register!"
msgstr ""

#: app/templates/auth/login.html:19
msgid "Forgot password?"
msgstr ""

#: app/templates/auth/register.html:16
msgid "Already a User?"
msgstr ""

#: app/templates/auth/register.html:16
msgid "Click to Sign In!"
msgstr ""

#: app/templates/auth/request_password_reset.html:6
msgid "Password Reset"
msgstr ""

#: app/templates/auth/request_password_reset.html:10
msgid "Please enter your email to receive a password reset link"
msgstr ""

#: app/templates/auth/reset_password.html:10
msgid "Please enter your new password"
msgstr ""

#: app/templates/auth/unconfirmed.html:5
msgid "Account Verification Pending"
msgstr ""

#: app/templates/auth/unconfirmed.html:9
msgid "Please check your inbox or junk folder for a confirmation link."
msgstr ""

#: app/templates/auth/unconfirmed.html:12
msgid "Didn't get the email?"
msgstr ""

#: app/templates/auth/unconfirmed.html:12
msgid "Resend"
msgstr ""

#: app/templates/email/activate.html:1
msgid "Please follow the below link to activate your account"
msgstr ""

#: app/templates/email/reset_password.html:1
msgid "Hi"
msgstr ""

#: app/templates/email/reset_password.html:2
msgid "To reset your password click on the following link"
msgstr ""

#: app/templates/email/reset_password.html:3
msgid "Reset password"
msgstr ""

#: app/templates/email/reset_password.html:4
msgid ""
"If you have not requested a password reset you can simply ignore this "
"message"
msgstr ""

#: app/templates/post/create.html:6
msgid "New Post"
msgstr ""

#: app/templates/post/read.html:19
msgid "Update"
msgstr ""

#: app/templates/post/read.html:21
msgid "Restore"
msgstr ""

#: app/templates/post/update.html:7
msgid "Edit Post"
msgstr ""

#: app/templates/post/update.html:15
msgid "Delete"
msgstr ""

#: app/templates/public/index.html:7
msgid "Posts"
msgstr ""

#: app/templates/public/profile.html:21
msgid "Last seen on"
msgstr ""

#: app/templates/public/profile.html:29
msgid "followers"
msgstr ""

#: app/templates/public/profile.html:29
msgid "following."
msgstr ""

#: app/templates/public/profile.html:39
msgid "Export posts"
msgstr ""

#: app/templates/public/profile.html:43
msgid "Send private message"
msgstr ""

#: app/templates/public/profile.html:49
msgid "Follow"
msgstr ""

#: app/templates/public/profile.html:56
msgid "Unfollow"
msgstr ""

#: app/templates/user/edit_profile.html:6
msgid "Edit Profile"
msgstr ""

#: app/templates/user/send_message.html:6
msgid "Send Message to"
msgstr ""

"""
