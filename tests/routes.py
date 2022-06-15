"""
tests.routes
============
"""
# pylint: disable=too-few-public-methods
import typing as t

from bs4 import BeautifulSoup
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from app.extensions import mail

from .utils import GetObjects, TestObject, UserTestObject


class CRUD:
    """Work with create, reading, updating, and deleting routes.

    :param client: Test client.
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
    """Handle all the authentication logic."""

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
            data={
                "password": user.password,
                "confirm_password": user.password,
            },
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
            data={"username": user.username, "password": user.password},
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
                    "username": user.username,
                    "email": user.email,
                    "password": user.password,
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


class Routes:
    """Collection of route classes."""

    def __init__(
        self, test_app: Flask, client: FlaskClient, get_objects: GetObjects
    ) -> None:
        self._posts = PostCRUD(client, get_objects)
        self._auth = AuthCRUD(test_app, client, get_objects)

    @property
    def posts(self) -> PostCRUD:
        """Work with /post."""
        return self._posts

    @property
    def auth(self) -> AuthCRUD:
        """Work with /auth."""
        return self._auth
