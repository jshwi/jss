"""
tests.routes
============
"""
# pylint: disable=too-few-public-methods
import contextlib
import typing as t

from bs4 import BeautifulSoup
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from app.extensions import mail

from .const import PASSWORD, USERNAME
from .utils import GetObjects, Recorder, TestObject, UserTestObject


class CRUD:
    """Work with create, reading, updating, and deleting routes.

    :param client: Test client.
    :param get_objects: Get test objects with db model attributes.
    """

    PREFIX = ""

    def __init__(self, client: FlaskClient, get_objects: GetObjects) -> None:
        self._client = client
        self._get_objects = get_objects

    def post(self, route: str, **kwargs: t.Any) -> TestResponse:
        """Route to post.

        :param route: CRUD route.
        :param kwargs: Kwargs to pass to ``post``.
        :return: Test ``Response`` object.
        """
        return self._client.post(f"{self.PREFIX}{route}", **kwargs)

    def get(
        self, route: t.Optional[str] = None, **kwargs: t.Any
    ) -> TestResponse:
        """Route to get.

        :param route: CRUD route.
        :param kwargs: Kwargs to pass to ``get``.
        :return: Test ``Response`` object.
        """
        _route = route if route is not None else ""
        return self._client.get(f"{self.PREFIX}{_route}", **kwargs)

    def add(
        self, route: str, test_object: TestObject, **kwargs: t.Any
    ) -> TestResponse:
        """Create a database entry.

        :param route: CRUD route.
        :param test_object: ``TestObject`` instance.
        :param kwargs: Kwargs to pass to ``post``.
        :return: Test ``Response`` object.
        """
        return self.post(route, data=vars(test_object), **kwargs)


class PostCRUD(CRUD):
    """Work with the post model."""

    PREFIX = "/post"

    def create(self, index: int, **kwargs: t.Any) -> TestResponse:
        """Add post to the database.

        :param index: ``PostTestObject`` index.
        :param kwargs: Kwargs to pass to ``post``.
        :return: Test ``Response`` object.
        """
        return self.add(
            "/create", self._get_objects.post(index)[index], **kwargs
        )

    def read(
        self, id: int, revision: t.Optional[int] = None, **kwargs: t.Any
    ) -> TestResponse:
        """Read post from database.

        :param id: ID of the model to update.
        :param revision: Version to get if provided.
        :param kwargs: Kwargs to pass to ``get``.
        :return: Test ``Response`` object.
        """
        _revision = "" if revision is None else f"?revision=0{revision}"
        return self.get(f"/{id}{_revision}", **kwargs)

    def update(
        self, index: int, post_id: int, **kwargs: t.Any
    ) -> TestResponse:
        """Update post in the database.

        :param index: ``PostTestObject`` index.
        :param post_id: ID of the post to update.
        :param kwargs: Kwargs to pass to ``post``.
        :return: Test ``Response`` object.
        """
        return self.add(
            f"/{post_id}/update",
            self._get_objects.post(index)[index],
            **kwargs,
        )

    def delete(self, post_id: int, **kwargs: t.Any) -> TestResponse:
        """Delete post from the database.

        :param post_id: ID of the post to delete.
        :param kwargs: Kwargs to pass to ``post``.
        :return: Test ``Response`` object.
        """
        return self.post(f"/{post_id}/delete", **kwargs)


class AuthCRUD(CRUD):
    """Handle all the authentication logic.

    :param test_app: Test application.
    :param client: Test client.
    :param get_objects: Get test objects with db model attributes.
    """

    PREFIX = "/auth"

    def __init__(
        self, test_app: Flask, client: FlaskClient, get_objects: GetObjects
    ) -> None:
        super().__init__(client, get_objects)
        self._test_app = test_app

    @staticmethod
    def parse_href(html: str) -> str:
        """Parse sent for password resets, verification, etc.

        :param html: HTML to parse.
        :return: href tag parsed from HTML.
        """
        return BeautifulSoup(html, features="html.parser").find("a")["href"]

    def follow_token(self, html: str) -> TestResponse:
        """Follow token sent for password resets, verification, etc.

        :param html: HTML str object.
        :return: Test ``Response`` object.
        """
        return self._client.get(self.parse_href(html), follow_redirects=True)

    def reset_password(
        self, index: int, html: str, **kwargs: t.Any
    ) -> TestResponse:
        """Reset password.

        :param index: ``UserTestObject`` index.
        :param html: HTML str object.
        :param kwargs: Kwargs to pass to ``post``.
        :return: Test ``Response`` object.
        """
        user = self._get_objects.user(index)[index]
        return self._client.post(
            self.parse_href(html),
            data={PASSWORD: user.password, "confirm_password": user.password},
            **kwargs,
        )

    def login(self, user: UserTestObject, **kwargs: t.Any) -> TestResponse:
        """Set client to the login state by user object.

        :param user: ``UserTestObject`` instance.
        :param kwargs: Kwargs to pass to ``post``.
        :return: Test ``Response`` object.
        """
        return self.post(
            "/login",
            data={USERNAME: user.username, PASSWORD: user.password},
            **kwargs,
        )

    def login_index(self, index, **kwargs: t.Any) -> TestResponse:
        """Set client to the login state.

        :param index: ``UserTestObject`` index.
        :param kwargs: Kwargs to pass to ``post``.
        :return: Test ``Response`` object.
        """
        return self.login(self._get_objects.user(index)[index], **kwargs)

    def logout(self, **kwargs: t.Any) -> TestResponse:
        """Log the current test user out.

        :param kwargs: Kwargs to pass to post.
        :return: Test ``Response`` object.
        """
        return self.get("/logout", **kwargs)

    def register(
        self, user: UserTestObject, confirm: bool = False, **kwargs: t.Any
    ) -> TestResponse:
        """Register a user object.

        :param user: ``UserTestObject`` instance.
        :param confirm: Confirm by following confirmation email.
        :param kwargs: Kwargs to pass to ``post``.
        :return: Test ``Response`` object.
        """
        with mail.record_messages() as outbox:
            response = self.post(
                "/register",
                data={
                    USERNAME: user.username,
                    "email": user.email,
                    PASSWORD: user.password,
                    "confirm_password": user.password,
                },
                **kwargs,
            )
            if confirm:
                with self._test_app.app_context():
                    return self.follow_token(outbox[0].html)

        return response

    def register_index(
        self, index: int, confirm: bool = False, **kwargs: t.Any
    ) -> TestResponse:
        """Register a user by index.

        :param index: ``UserTestObject`` index.
        :param confirm: Confirm by following confirmation email.
        :param kwargs: Kwargs to pass to ``post``.
        :return: Test ``Response`` object.
        """
        return self.register(
            self._get_objects.user(index)[index], confirm, **kwargs
        )

    def request_password_reset(
        self, index: int, **kwargs: t.Any
    ) -> TestResponse:
        """Request user password reset.

        :param index: ``UserTestObject`` index.
        :param kwargs: Kwargs to pass to ``post``.
        :return: Response object.
        """
        return self.post(
            "/request_password_reset",
            data={"email": self._get_objects.user(index)[index].email},
            **kwargs,
        )


class UserCRUD(CRUD):
    """Handle all the user logic."""

    PREFIX = "/user"

    def edit(
        self,
        username: t.Optional[str] = None,
        about_me: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> TestResponse:
        """Edit logged-in test user profile page.

        :param username: New username if provided.
        :param about_me: New ``About Me`` info is provided.
        :param kwargs: Kwargs to pass to post.
        :return: Test ``Response`` object.
        """
        data = {}
        if username is not None:
            data[USERNAME] = username

        if about_me is not None:
            data["about_me"] = about_me

        return self.post("/profile/edit", data=data, **kwargs)

    def send_message(self, index: int, **kwargs: t.Any) -> TestResponse:
        """Send messages to test user from logged-in test user.

        :param index: ``UserTestObject`` index to send message to.
        :param kwargs: Kwargs to pass to post.
        :return: Test ``Response`` object.
        """
        user = self._get_objects.user(index)[index]
        return self.post(
            f"/send_message/{user.username}",
            data={"message": user.message},
            **kwargs,
        )

    def notifications(self, **kwargs: t.Any) -> TestResponse:
        """Get request to notifications route.

        :param kwargs: Kwargs to pass to post.
        :return: Test ``Response`` object.
        """
        return self.get("/notifications", **kwargs)

    def messages(self, **kwargs: t.Any) -> TestResponse:
        """Get request to /messages.

        :param kwargs: Kwargs to pass to post.
        :return: Test ``Response`` object.
        """
        return self.get("/messages", **kwargs)


class AdminCRUD(CRUD):
    """Handle all admin logic."""

    PREFIX = "/admin"

    def users(self, **kwargs: t.Any) -> TestResponse:
        """Get result from users endpoint.

        :param kwargs: Kwargs to pass to get.
        :return: Test ``Response`` object.
        """
        return self.get("/users", **kwargs)


class ProfileCRUD(CRUD):
    """Handle all profile logic."""

    PREFIX = "/profile"

    def user(self, index: int, **kwargs: t.Any) -> TestResponse:
        """Get user profile.

        :param index: ``UserTestObject`` index.
        :param kwargs: Kwargs to pass to get.
        :return: Test ``Response`` object.
        """
        return self.get(
            f"/{self._get_objects.user(index)[index].username}", **kwargs
        )


class RedirectCRUD(CRUD):
    """Handle /redirect.

    :param test_app: Test application.
    :param client: Test client.
    :param get_objects: Get test objects with db model attributes.
    """

    PREFIX = "/redirect"

    def __init__(
        self, test_app: Flask, client: FlaskClient, get_objects: GetObjects
    ) -> None:
        super().__init__(client, get_objects)
        self._test_app = test_app

    def follow(self, index: int, **kwargs) -> TestResponse:
        """Follow another user.

        :param index: ``UserTestObject`` index.
        :param kwargs: Kwargs to pass to post.
        :return: Test ``Response`` object.
        """
        return self.post(
            f"/follow/{self._get_objects.user(index)[index].username}",
            **kwargs,
        )

    def unfollow(self, index: int, **kwargs) -> TestResponse:
        """Unfollow another user.

        :param index: ``UserTestObject`` index.
        :param kwargs: Kwargs to pass to post.
        :return: Test ``Response`` object.
        """
        return self.post(
            f"/unfollow/{self._get_objects.user(index)[index].username}",
            **kwargs,
        )

    @contextlib.contextmanager
    def _patch_test_app(
        self, attr: str, value: object
    ) -> t.Generator[Flask, None, None]:
        original = getattr(self._test_app, attr)
        setattr(self._test_app, attr, value)
        yield self._test_app
        setattr(self._test_app, attr, original)

    def add_export_posts_task(
        self, task_id: str, **kwargs: t.Any
    ) -> TestResponse:
        """Add task to database.

        :param task_id: ID to give the task.
        :param kwargs: Kwargs to pass to get.
        :return: Test ``Response`` object.
        """
        task_queue = Recorder()  # type: ignore
        task_queue.enqueue = Recorder()  # type: ignore
        task_queue.enqueue.get_id = lambda: task_id  # type: ignore
        with self._patch_test_app("task_queue", task_queue):
            return self.get("/export_posts", **kwargs)


class Routes:
    """Collection of route classes.

    :param test_app: Test application.
    :param client: Test client.
    :param get_objects: Get test objects with db model attributes.
    """

    def __init__(
        self, test_app: Flask, client: FlaskClient, get_objects: GetObjects
    ) -> None:
        self._posts = PostCRUD(client, get_objects)
        self._auth = AuthCRUD(test_app, client, get_objects)
        self._user = UserCRUD(client, get_objects)
        self._admin = AdminCRUD(client, get_objects)
        self._profile = ProfileCRUD(client, get_objects)
        self._redirect = RedirectCRUD(test_app, client, get_objects)

    @property
    def posts(self) -> PostCRUD:
        """Work with /post."""
        return self._posts

    @property
    def auth(self) -> AuthCRUD:
        """Work with /auth."""
        return self._auth

    @property
    def user(self) -> UserCRUD:
        """Work with /user."""
        return self._user

    @property
    def admin(self) -> AdminCRUD:
        """Work with /admin."""
        return self._admin

    @property
    def profile(self) -> ProfileCRUD:
        """Work with /profile."""
        return self._profile

    @property
    def redirect(self) -> RedirectCRUD:
        """Work with /redirect."""
        return self._redirect
