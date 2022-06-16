"""
tests.routes
============
"""
# pylint: disable=too-few-public-methods
import typing as t

from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from .utils import GetObjects, TestObject


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


class Routes:
    """Collection of route classes."""

    def __init__(self, client: FlaskClient, get_objects: GetObjects) -> None:
        self._posts = PostCRUD(client, get_objects)

    @property
    def posts(self) -> PostCRUD:
        """Work with /post."""
        return self._posts
