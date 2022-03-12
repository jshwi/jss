"""
app.dom.redirect
================

Frequently used redirects.
"""
import typing as t

from flask import redirect, url_for
from werkzeug import Response


class _Redirect:
    """Collection of redirects."""

    @classmethod
    def prefix(cls) -> str:
        """Prefix the ``url_for`` with the name of the child class."""
        return cls.__name__.lower()

    @classmethod
    def redirect(cls, target: str, **kwargs: t.Any) -> Response:
        """Response object leading to target route.

        :param target: Target route.
        :param kwargs: Keyword arguments to add to query string.
        :return: Response object.
        """
        return redirect(url_for(f"{cls.prefix()}.{target}", **kwargs))


def index(**kwargs) -> Response:
    """Response object leading to index route.

    :param kwargs: Keyword arguments to add to query string.
    :return: Response object.
    """
    return redirect(url_for("index", **kwargs))


class Auth(_Redirect):
    """Redirects to auth routes."""

    @classmethod
    def login(cls, **kwargs) -> Response:
        """Response object leading to auth/login route.

        :param kwargs: Keyword arguments to add to query string.
        :return: Response object.
        """
        return cls.redirect("login", **kwargs)

    @classmethod
    def unconfirmed(cls, **kwargs) -> Response:
        """Response object leading to auth/unconfirmed route.

        :param kwargs: Keyword arguments to add to query string.
        :return: Response object.
        """
        return cls.redirect("unconfirmed", **kwargs)


class Public(_Redirect):
    """Redirects to public routes."""

    @classmethod
    def profile(cls, **kwargs) -> Response:
        """Response object leading to public/profile route.

        :param kwargs: Keyword arguments to add to query string.
        :return: Response object.
        """
        return cls.redirect("profile", **kwargs)
