"""
app.config
==========

Most configuration is set via environment variables as per
https://12factor.net/config:
"""
# pylint: disable=too-many-public-methods,invalid-name
import datetime
import typing as t
from pathlib import Path

import tomli
from environs import Env
from flask import Flask

env = Env()

env.read_env()


class Config:
    """Load environment."""

    @property
    def ENV(self) -> str:
        """Default to production."""
        return env.str("FLASK_ENV", default="production")

    @property
    def DEBUG(self) -> bool:
        """Value depends on the ``FLASK_ENV`` environment."""
        return env.bool("FLASK_DEBUG", default=self.ENV == "development")

    @property
    def TESTING(self) -> bool:
        """Value depends on the ``FLASK_ENV`` environment."""
        return env.bool("TESTING", default=self.ENV == "testing")

    @property
    def DATABASE_URL(self) -> t.Optional[str]:
        """Database location."""
        return env.str("DATABASE_URL", default=None)

    @property
    def SECRET_KEY(self) -> t.Optional[str]:
        """Value is not public."""
        return env.str("SECRET_KEY", default=None)

    @property
    def SEND_FILE_MAX_AGE_DEFAULT(self) -> int:
        """Read from environment."""
        return env.int("SEND_FILE_MAX_AGE_DEFAULT", default=31556926)

    @property
    def BCRYPT_LOG_ROUNDS(self) -> int:
        """Defaults to 13."""
        return env.int("BCRYPT_LOG_ROUNDS", default=13)

    @property
    def DEBUG_TB_ENABLED(self) -> bool:
        """When ``DEBUG`` is True enable ``TB`` (toolbar)."""
        return env.bool("DEBUG_TB_ENABLED", default=self.DEBUG)

    @property
    def DEBUG_TB_INTERCEPT_REDIRECTS(self) -> bool:
        """Remains False."""
        return env.bool("DEBUG_TB_INTERCEPT_REDIRECTS", default=False)

    @property
    def FLASK_STATIC_DIGEST_HOST_URL(self) -> t.Optional[str]:
        """Set to a value such as https://cdn.example.com.

        Prefix your static path with this URL. This would be useful if
        you host your files from a CDN. Make sure to include the
        protocol (aka. https://).
        """
        return env.str("FLASK_STATIC_DIGEST_HOST_URL", default=None)

    @property
    def FLASK_STATIC_DIGEST_BLACKLIST_FILTER(self) -> t.List[str]:
        """Do not md5 tag added extensions.

        eg: [".htm", ".html", ".txt"]. Make sure to include the ".".
        """
        return env.list("FLASK_STATIC_DIGEST_BLACKLIST_FILTER", default=[])

    @property
    def FLASK_STATIC_DIGEST_GZIP_FILES(self) -> bool:
        """When set to False then gzipped files will not be created.

        Static files will still get md5 tagged.
        """
        return env.bool("FLASK_STATIC_DIGEST_GZIP_FILES", default=True)

    @property
    def CACHE_TYPE(self) -> str:
        """Can be "memcached", "redis", etc."""
        return env.str("CACHE_TYPE", default="simple")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Alias for ``DATABASE_URL.``"""
        return env.str("SQLALCHEMY_DATABASE_URI", default=self.DATABASE_URL)

    @property
    def SQLALCHEMY_TRACK_MODIFICATIONS(self) -> bool:
        """Set to False by default: Can be a resource drain."""
        return env.bool("SQlALCHEMY_TRACK_MODIFICATIONS", default=False)

    @property
    def DEFAULT_MAIL_SENDER(self) -> t.Optional[str]:
        """Default mail sender."""
        return env.str("DEFAULT_MAIL_SENDER", default=None)

    @property
    def MAIL_SUBJECT_PREFIX(self) -> str:
        """str object to prefix mail client's subject line with."""
        return env.str("MAIL_SUBJECT_PREFIX", default="")

    @property
    def ADMINS(self) -> t.Optional[t.List[str]]:
        """List of web admins."""
        return env.list("ADMINS", default=[])

    @property
    def WTF_CSRF_ENABLED(self) -> bool:
        """Cross-Site Request Forgery: Switch off for testing."""
        return env.bool("WTF_CSRF_ENABLED", default=not self.TESTING)

    @property
    def WTF_CSRF_SECRET_KEY(self) -> str:
        """Secret keys for signing CSRF tokens."""
        return env.str("WTF_CSRF_SECRET_KEY", self.SECRET_KEY)

    @property
    def SECURITY_PASSWORD_SALT(self) -> t.Optional[str]:
        """Combined with the unique salt generated for each password."""
        return env.str("SECURITY_PASSWORD_SALT", default=self.SECRET_KEY)

    @property
    def MAIL_SERVER(self) -> str:
        """Mail server to send mail from."""
        return env.str("MAIL_SERVER", default=None)

    @property
    def MAIL_PORT(self) -> int:
        """Mail port to send mail from."""
        return env.int("MAIL_PORT", default=25)

    @property
    def MAIL_USE_TLS(self) -> bool:
        """Use TLS: Defaults to False."""
        return env.bool("MAIL_USER_TLS", default=False)

    @property
    def MAIL_USE_SSL(self) -> bool:
        """Use SSL: Defaults to False."""
        return env.bool("MAIL_USER_SSL", default=False)

    @property
    def MAIL_DEBUG(self) -> bool:
        """Mail debug mode: Default to same as ``FLASK_DEBUG``."""
        return env.bool("MAIL_DEBUG", default=self.DEBUG)

    @property
    def MAIL_USERNAME(self) -> t.Optional[str]:
        """Username of sender."""
        return env.str("MAIL_USERNAME", default=None)

    @property
    def MAIL_PASSWORD(self) -> t.Optional[str]:
        """Password of sender."""
        return env.str("MAIL_PASSWORD", default=None)

    @property
    def POSTS_PER_PAGE(self) -> int:
        """Posts to paginate per page."""
        return env.int("POSTS_PER_PAGE", default=25)

    @property
    def REDIS_URL(self) -> str:
        """URL to ``Redis`` server."""
        return env.str("REDIS_URL", default="redis://")

    @property
    def RESERVED_USERNAMES(self) -> t.List[str]:
        """List of names that cannot be registered the standard way."""
        return env.list("RESERVED_USERNAMES", default=[])

    @property
    def BRAND(self) -> str:
        """Display in navbar and on browser tabs."""
        return env.str("BRAND", default="")

    @property
    def LICENSE(self) -> Path:
        """Path to LICENSE file."""
        return env.path(
            "LICENSE",
            default=Path(__file__).absolute().parent.parent / "LICENSE",
        )

    @property
    def PYPROJECT_TOML(self) -> Path:
        """Path to LICENSE file."""
        return env.path(
            "PYPROJECT_TOML",
            default=Path(__file__).absolute().parent.parent / "pyproject.toml",
        )

    @property
    def COPYRIGHT(self) -> t.Optional[str]:
        """Return the copyright line from LICENSE else None."""
        declaration = None
        if self.LICENSE.is_file():
            with open(self.LICENSE, encoding="utf-8") as fin:
                for line in fin.read().splitlines():
                    if "Copyright" in line:
                        declaration = line

        return env.str("COPYRIGHT", default=declaration)

    @property
    def COPYRIGHT_YEAR(self) -> str:
        """Get the copyright year for this app.

        Default is the current year if no LICENSE can be found. If
        LICENSE can be found the default year is parsed from it.

        If ``COPYRIGHT_YEAR`` environment variables is set then that
        is returned.
        """
        year = datetime.datetime.now().strftime("%Y")
        if self.COPYRIGHT is not None:
            year = self.COPYRIGHT.split()[2]

        return env.str("COPYRIGHT_YEAR", default=year)

    @property
    def COPYRIGHT_AUTHOR(self) -> str:
        """Get the copyright author for this app.

        Default is an empty str if no LICENSE can be found. If LICENSE
        can be found the default is parsed from it.

        If ``COPYRIGHT_AUTHOR`` environment variables is set then that
        is returned.
        """
        author = ""
        if self.COPYRIGHT is not None:
            author = " ".join(self.COPYRIGHT.split()[3:])

        return env.str("COPYRIGHT_AUTHOR", default=author)

    @property
    def COPYRIGHT_EMAIL(self) -> str:
        """Get the copyright author's email for this app.

        Default is an empty str if no setup file can be found.
        If a setup file can be found the default is parsed from it.

        If ``COPYRIGHT_EMAIL`` environment variables is set, then that
        is returned.
        """
        email = ""
        if self.PYPROJECT_TOML.is_file():
            obj = tomli.loads(self.PYPROJECT_TOML.read_text())
            authors = obj.get("tool", {}).get("poetry", {}).get("authors", [])
            if authors:
                email = authors[0].split()[1][1:-1]

        return env.str("COPYRIGHT_EMAIL", default=email)

    @property
    def NAVBAR_HOME(self) -> bool:
        """Include ``Home`` in navbar as opposed to only the brand."""
        return env.bool("NAVBAR_HOME", default=True)

    @property
    def NAVBAR_ICONS(self) -> bool:
        """Display certain links in navbar as icons instead of text."""
        return env.bool("NAVBAR_ICONS", default=False)

    @property
    def NAVBAR_USER_DROPDOWN(self) -> bool:
        """Display logged-in user links as dropdown."""
        return env.bool("NAVBAR_USER_DROPDOWN", default=False)

    @property
    def SESSION_COOKIE_HTTPONLY(self) -> bool:
        """Set session-cookie HttpOnly parameter; Defaults to True."""
        return env.bool("SESSION_COOKIE_HTTPONLY", default=True)

    @property
    def SESSION_COOKIE_SECURE(self) -> bool:
        """Set session-cookie secure parameter; Defaults to True."""
        return env.bool("SESSION_COOKIE_SECURE", default=True)

    @property
    def SESSION_COOKIE_SAMESITE(self) -> str:
        """Set session-cookie SAMESITE parameter; Defaults to strict."""
        return env.str("REMEMBER_COOKIE_SAMESITE", default="strict")

    @property
    def REMEMBER_COOKIE_SECURE(self) -> bool:
        """Set remember-cookie secure parameter; Defaults to True.

        The cookie for the ``Remember Me`` checkbox in logins.
        """
        return env.bool("REMEMBER_COOKIE_SECURE", default=True)

    @property
    def PREFERRED_URL_SCHEME(self) -> str:
        """HTTPS or HTTP."""
        return env.str("PREFERRED_URL_SCHEME", default="https")

    @property
    def CSP(self) -> t.Dict[str, t.Union[str, t.List[str]]]:
        """Content Security Policy."""
        return env.dict("CSP", default={})

    @property
    def CSP_REPORT_ONLY(self) -> bool:
        """Do not enforce CSP, report violations only."""
        return env.bool("CSP_REPORT_ONLY", default=True)

    @property
    def CSP_REPORT_URI(self) -> str:
        """URI to report CSP violations to."""
        return env.str("CSP_REPORT_URI", default="/report/csp_violations")

    @property
    def BOOTSTRAP_SERVE_LOCAL(self) -> bool:
        """Serve local CSS."""
        return env.bool("BOOTSTRAP_SERVE_LOCAL", default=True)


def init_app(app: Flask) -> None:
    """Register config for ``Flask`` app.

    Accessible within app as ``current_app.config["CONFIG_KEY"]``
    through application context, or ``app.config["CONFIG_KEY"]`` if
    passed to a function as an arg such as this one.

    While using ``Jinja`` templates config is accessible simply through
    {{ config["CONFIG_KEY"] }}.

    :param app: Application factory object.
    """
    app.config.from_object(Config())
