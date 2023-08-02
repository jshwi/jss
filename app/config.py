"""
app.config
==========

Most configuration is set via environment variables as per
https://12factor.net/config:
"""
# pylint: disable=too-many-public-methods,invalid-name
from __future__ import annotations

import datetime
from pathlib import Path

import tomli
from environs import Env
from flask import Flask


class Config(Env):
    """The application's configuration object.

    :param root_path: The application's filesystem, starting at the
        root.
    """

    def __init__(self, root_path: Path) -> None:
        super().__init__()
        self._root_path = root_path

    @property
    def DEBUG(self) -> bool:
        """Debug mode."""
        return self.bool("FLASK_DEBUG", default=False)

    @property
    def TESTING(self) -> bool:
        """Testing mode."""
        return self.bool("TESTING", default=False)

    @property
    def DATABASE_URL(self) -> str:
        """Database location."""
        return self.str("DATABASE_URL", default="sqlite:///:memory:")

    @property
    def SECRET_KEY(self) -> str | None:
        """Value is not public."""
        return self.str("SECRET_KEY", default=None)

    @property
    def SEND_FILE_MAX_AGE_DEFAULT(self) -> int:
        """Read from environment."""
        return self.int("SEND_FILE_MAX_AGE_DEFAULT", default=31556926)

    @property
    def BCRYPT_LOG_ROUNDS(self) -> int:
        """Defaults to 13."""
        return self.int("BCRYPT_LOG_ROUNDS", default=13)

    @property
    def DEBUG_TB_ENABLED(self) -> bool:
        """When ``DEBUG`` is True enable ``TB`` (toolbar)."""
        return self.bool("DEBUG_TB_ENABLED", default=self.DEBUG)

    @property
    def DEBUG_TB_INTERCEPT_REDIRECTS(self) -> bool:
        """Remains False."""
        return self.bool("DEBUG_TB_INTERCEPT_REDIRECTS", default=False)

    @property
    def FLASK_STATIC_DIGEST_HOST_URL(self) -> str | None:
        """Set to a value such as https://cdn.example.com.

        Prefix your static path with this URL. This would be useful if
        you host your files from a CDN. Make sure to include the
        protocol (aka. https://).
        """
        return self.str("FLASK_STATIC_DIGEST_HOST_URL", default=None)

    @property
    def FLASK_STATIC_DIGEST_BLACKLIST_FILTER(self) -> list[str]:
        """Do not md5 tag added extensions.

        eg: [".htm", ".html", ".txt"]. Make sure to include the ".".
        """
        return self.list("FLASK_STATIC_DIGEST_BLACKLIST_FILTER", default=[])

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Alias for ``DATABASE_URL.``"""
        # this was the default in 2.x.x, now if this does not get set
        # before a certain action a runtime error is raised
        return self.str(
            "SQLALCHEMY_DATABASE_URI",
            default=self.DATABASE_URL.replace("postgres://", "postgresql://"),
        )

    @property
    def SQLALCHEMY_TRACK_MODIFICATIONS(self) -> bool:
        """Set to False by default: Can be a resource drain."""
        return self.bool("SQlALCHEMY_TRACK_MODIFICATIONS", default=False)

    @property
    def DEFAULT_MAIL_SENDER(self) -> str | None:
        """Default mail sender."""
        return self.str("DEFAULT_MAIL_SENDER", default=None)

    @property
    def MAIL_SUBJECT_PREFIX(self) -> str:
        """Str object to prefix mail client's subject line with."""
        return self.str("MAIL_SUBJECT_PREFIX", default="")

    @property
    def ADMINS(self) -> list[str]:
        """List of web admins."""
        return self.list("ADMINS", default=[])

    @property
    def WTF_CSRF_ENABLED(self) -> bool:
        """Cross-Site Request Forgery: Switch off for testing."""
        return self.bool("WTF_CSRF_ENABLED", default=not self.TESTING)

    @property
    def WTF_CSRF_SECRET_KEY(self) -> str:
        """Secret keys for signing CSRF tokens."""
        return self.str("WTF_CSRF_SECRET_KEY", self.SECRET_KEY)

    @property
    def SECURITY_PASSWORD_SALT(self) -> str | None:
        """Combined with the unique salt generated for each password."""
        return self.str("SECURITY_PASSWORD_SALT", default=self.SECRET_KEY)

    @property
    def MAIL_SERVER(self) -> str:
        """Mail server to send mail from."""
        return self.str("MAIL_SERVER", default=None)

    @property
    def MAIL_PORT(self) -> int:
        """Mail port to send mail from."""
        return self.int("MAIL_PORT", default=25)

    @property
    def MAIL_USE_TLS(self) -> bool:
        """Use TLS: Defaults to False."""
        return self.bool("MAIL_USER_TLS", default=False)

    @property
    def MAIL_USE_SSL(self) -> bool:
        """Use SSL: Defaults to False."""
        return self.bool("MAIL_USER_SSL", default=False)

    @property
    def MAIL_USERNAME(self) -> str | None:
        """Username of sender."""
        return self.str("MAIL_USERNAME", default=None)

    @property
    def MAIL_PASSWORD(self) -> str | None:
        """Password of sender."""
        return self.str("MAIL_PASSWORD", default=None)

    @property
    def POSTS_PER_PAGE(self) -> int:
        """Posts to paginate per page."""
        return self.int("POSTS_PER_PAGE", default=25)

    @property
    def REDIS_URL(self) -> str:
        """URL to ``Redis`` server."""
        return self.str("REDIS_URL", default="redis://")

    @property
    def RESERVED_USERNAMES(self) -> list[str]:
        """List of names that cannot be registered the standard way."""
        return self.list("RESERVED_USERNAMES", default=[])

    @property
    def BRAND(self) -> str:
        """Display in navbar and on browser tabs."""
        return self.str("BRAND", default="")

    @property
    def LICENSE(self) -> Path:
        """Path to LICENSE file."""
        return self.path("LICENSE", default=self._root_path.parent / "LICENSE")

    @property
    def PYPROJECT_TOML(self) -> Path:
        """Path to LICENSE file."""
        return self.path(
            "PYPROJECT_TOML", default=self._root_path.parent / "pyproject.toml"
        )

    @property
    def COPYRIGHT(self) -> str | None:
        """Return the copyright line from LICENSE else None."""
        declaration = None
        if self.LICENSE.is_file():
            with open(self.LICENSE, encoding="utf-8") as fin:
                for line in fin.read().splitlines():
                    if "Copyright" in line:
                        declaration = line

        return self.str("COPYRIGHT", default=declaration)

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

        return self.str("COPYRIGHT_YEAR", default=year)

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

        return self.str("COPYRIGHT_AUTHOR", default=author)

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

        return self.str("COPYRIGHT_EMAIL", default=email)

    @property
    def NAVBAR_HOME(self) -> bool:
        """Include ``Home`` in navbar as opposed to only the brand."""
        return self.bool("NAVBAR_HOME", default=True)

    @property
    def NAVBAR_ICONS(self) -> bool:
        """Display certain links in navbar as icons instead of text."""
        return self.bool("NAVBAR_ICONS", default=False)

    @property
    def NAVBAR_USER_DROPDOWN(self) -> bool:
        """Display logged-in user links as dropdown."""
        return self.bool("NAVBAR_USER_DROPDOWN", default=False)

    @property
    def SESSION_COOKIE_HTTPONLY(self) -> bool:
        """Set session-cookie HttpOnly parameter; Defaults to True."""
        return self.bool("SESSION_COOKIE_HTTPONLY", default=True)

    @property
    def SESSION_COOKIE_SECURE(self) -> bool:
        """Set session-cookie secure parameter; Defaults to True."""
        return self.bool("SESSION_COOKIE_SECURE", default=True)

    @property
    def SESSION_COOKIE_SAMESITE(self) -> str:
        """Set session-cookie SAMESITE parameter; Defaults to strict."""
        return self.str("REMEMBER_COOKIE_SAMESITE", default="strict")

    @property
    def REMEMBER_COOKIE_SECURE(self) -> bool:
        """Set remember-cookie secure parameter; Defaults to True.

        The cookie for the ``Remember Me`` checkbox in logins.
        """
        return self.bool("REMEMBER_COOKIE_SECURE", default=True)

    @property
    def PREFERRED_URL_SCHEME(self) -> str:
        """HTTPS or HTTP."""
        return self.str("PREFERRED_URL_SCHEME", default="https")

    @property
    def CSP(self) -> dict[str, str | list[str]]:
        """Content Security Policy."""
        return self.dict("CSP", default={})

    @property
    def CSP_REPORT_ONLY(self) -> bool:
        """Do not enforce CSP, report violations only."""
        return self.bool("CSP_REPORT_ONLY", default=True)

    @property
    def CSP_REPORT_URI(self) -> str:
        """URI to report CSP violations to."""
        return self.str("CSP_REPORT_URI", default="/report/csp_violations")

    @property
    def BOOTSTRAP_SERVE_LOCAL(self) -> bool:
        """Serve local CSS."""
        return self.bool("BOOTSTRAP_SERVE_LOCAL", default=True)

    @property
    def SIGNATURE(self) -> str:
        """Signature to sign off emails with."""
        return self.str("SIGNATURE", default=self.BRAND)

    @property
    def ADMIN_SECRET(self) -> str:
        """Password for initialized admin user."""
        return self.str("ADMIN_SECRET", default=None)

    @property
    def TRANSLATIONS_DIR(self) -> Path:
        """Dir to store translations in."""
        return self.path(
            "TRANSLATIONS_DIR", default=self._root_path / "translations"
        )

    @property
    def LANGUAGES(self) -> list[str]:
        """Supported languages."""
        default = ["en"]
        if self.TRANSLATIONS_DIR.is_dir():
            default.extend([p.name for p in self.TRANSLATIONS_DIR.iterdir()])

        return self.list("LANGUAGES", default=default)

    @property
    def SHOW_POSTS(self) -> bool:
        """Show posts from database."""
        return self.bool("SHOW_POSTS", default=True)

    @property
    def TITLE(self) -> str:
        """Header for page."""
        return self.str("TITLE", default="")

    @property
    def SHOW_REGISTER(self) -> bool:
        """Show register option."""
        return self.bool("SHOW_REGISTER", default=True)

    @property
    def SHOW_PAYMENT(self) -> bool:
        """Show payment option."""
        return self.bool("SHOW_PAYMENT", default=False)

    @property
    def STRIPE_SECRET_KEY(self) -> str:
        """Secret key for Stripe API."""
        return self.str("STRIPE_SECRET_KEY", default=None)

    @property
    def PAYMENT_OPTIONS(self) -> dict[str, str]:
        """Options to pass to Stripe's API."""
        return self.dict("PAYMENT_OPTIONS", default={"price": "None"})

    @property
    def MAX_CONTENT_LENGTH(self) -> int:
        """Max content length for file uploads."""
        return self.int("MAX_CONTENT_LENGTH", default=1024 * 1024)

    @property
    def UPLOAD_EXTENSIONS(self) -> list[str]:
        """Extensions allowed for upload."""
        return self.list(
            "UPLOAD_EXTENSIONS",
            default=[".txt", ".pdf", ".png", ".jpg", ".jpeg", ".gif"],
        )

    @property
    def STATIC_FOLDER(self) -> Path:
        """Path to static files."""
        return self.path("STATIC_FOLDER", default=self._root_path / "static")

    @property
    def UPLOAD_PATH(self) -> Path:
        """Path to upload file to."""
        return self.path("UPLOAD_PATH", default=self.STATIC_FOLDER / "uploads")

    @property
    def SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS(self) -> bool:
        """Generate list of rules without params."""
        return self.bool("SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS", default=True)


def init_app(app: Flask) -> None:
    """Register config for ``Flask`` app.

    Accessible within app as ``current_app.config["CONFIG_KEY"]``
    through application context, or ``app.config["CONFIG_KEY"]`` if
    passed to a function as an arg such as this one.

    While using ``Jinja`` templates config is accessible simply through
    {{ config["CONFIG_KEY"] }}.

    :param app: Application factory object.
    """
    config = Config(Path(app.root_path))
    config.read_env()
    app.config.from_object(config)
    app.static_folder = app.config["STATIC_FOLDER"]
