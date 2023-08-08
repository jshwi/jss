"""
app.config
==========

Most configuration is set via environment variables as per
https://12factor.net/config:
"""
# pylint: disable=too-many-public-methods,invalid-name
from __future__ import annotations

from pathlib import Path

import tomli
from environs import Env
from flask import Flask


class Config(Env):
    """The application's configuration object.

    List objects are comma separated values.

    .. code-block:: console

        LIST=comma,separated,values

    Dict objects are comma separated variable assignments.

    .. code-block:: console

        DICT=comma=0,separated=1,values=2

    :param root_path: The application's filesystem, starting at the
        root.
    """

    def __init__(self, root_path: Path) -> None:
        super().__init__()
        self._root_path = root_path

    @property
    def DEBUG(self) -> bool:
        """Run the application in debug mode.

        Default value is ``False``.
        """
        return self.bool("FLASK_DEBUG", default=False)

    @property
    def TESTING(self) -> bool:
        """Testing mode.

        Default value is ``False``.
        """
        return self.bool("TESTING", default=False)

    @property
    def DATABASE_URL(self) -> str:
        """Database URL.

        Default value is ``None``.
        """
        return self.str("DATABASE_URL", default="sqlite:///:memory:")

    @property
    def SECRET_KEY(self) -> str | None:
        """Key for security related needs.

        Used for securely signing the session cookie and can be used for
        any other security related needs by extensions or the
        application. It should be a long random bytes or str.
        For example:

        .. code-block:: console

            $ python -c 'import secrets; print(secrets.token_hex())'
            '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d547...'

        Default value is ``None``.
        """
        return self.str("SECRET_KEY", default=None)

    @property
    def SEND_FILE_MAX_AGE_DEFAULT(self) -> int:
        """Timedelta used as ``cache_timeout`` for ``send_file`` funcs.

        This configuration variable can also be set with an integer
        value used as seconds.

        Default value is ``31556926``.
        """
        return self.int("SEND_FILE_MAX_AGE_DEFAULT", default=31556926)

    @property
    def BCRYPT_LOG_ROUNDS(self) -> int:
        """Determine the complexity of bcrypt encryption.

        see bcrypt for more details.

        Default value is ``13``.
        """
        return self.int("BCRYPT_LOG_ROUNDS", default=13)

    @property
    def DEBUG_TB_ENABLED(self) -> bool:
        """When ``DEBUG`` is True enable ``TB`` (toolbar)."""
        return self.bool("DEBUG_TB_ENABLED", default=self.DEBUG)

    @property
    def DEBUG_TB_INTERCEPT_REDIRECTS(self) -> bool:
        """Debug-toolbar to intercept redirects.

        Default value is ``False``.
        """
        return self.bool("DEBUG_TB_INTERCEPT_REDIRECTS", default=False)

    @property
    def FLASK_STATIC_DIGEST_HOST_URL(self) -> str | None:
        """Set to a value such as https://cdn.example.com.

        Prefix your static path with this URL. This would be useful if
        you host your files from a CDN. Make sure to include the
        protocol (aka. https://).

        Default value is ``None``.
        """
        return self.str("FLASK_STATIC_DIGEST_HOST_URL", default=None)

    @property
    def FLASK_STATIC_DIGEST_BLACKLIST_FILTER(self) -> list[str]:
        """Do not md5 tag added extensions.

        eg: [".htm", ".html", ".txt"]. Make sure to include the ".".

        Default value is ``[]``.
        """
        return self.list("FLASK_STATIC_DIGEST_BLACKLIST_FILTER", default=[])

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """The database URI that should be used for the connection.

        Default value is ``"sqlite:///:memory:"``.
        """
        # this was the default in 2.x.x, now if this does not get set
        # before a certain action a runtime error is raised
        return self.str(
            "SQLALCHEMY_DATABASE_URI",
            default=self.DATABASE_URL.replace("postgres://", "postgresql://"),
        )

    @property
    def SQLALCHEMY_TRACK_MODIFICATIONS(self) -> bool:
        """Track modifications of objects and emit signals.

        This requires extra memory and should be disabled if not needed.

        Default value is ``False``.
        """
        return self.bool("SQlALCHEMY_TRACK_MODIFICATIONS", default=False)

    @property
    def DEFAULT_MAIL_SENDER(self) -> str | None:
        """Default mail sender.

        Default value is ``None``.
        """
        return self.str("DEFAULT_MAIL_SENDER", default=None)

    @property
    def MAIL_SUBJECT_PREFIX(self) -> str:
        """Prefix for mail subject.

        Default value is ``""``.
        """
        return self.str("MAIL_SUBJECT_PREFIX", default="")

    @property
    def ADMINS(self) -> list[str]:
        """List of web admins.

        Default value is ``[]``.
        """
        return self.list("ADMINS", default=[])

    @property
    def WTF_CSRF_ENABLED(self) -> bool:
        """Cross-Site Request Forgery: Switch off for testing.

        Default value is ``TESTING``.
        """
        return self.bool("WTF_CSRF_ENABLED", default=not self.TESTING)

    @property
    def WTF_CSRF_SECRET_KEY(self) -> str:
        """Secret key for signing CSRF tokens.

        Default value is ``SECRET_KEY``.
        """
        return self.str("WTF_CSRF_SECRET_KEY", self.SECRET_KEY)

    @property
    def SECURITY_PASSWORD_SALT(self) -> str | None:
        """Specifies the HMAC salt.

        This is only used if the password hash type is set to something
        other than plain text.

        Default value is ``SECRET_KEY``.
        """
        return self.str("SECURITY_PASSWORD_SALT", default=self.SECRET_KEY)

    @property
    def MAIL_SERVER(self) -> str:
        """Mail server to send mail from.

        Default value is ``None``.
        """
        return self.str("MAIL_SERVER", default=None)

    @property
    def MAIL_PORT(self) -> int:
        """Mail port to send mail from.

        Default value is ``25``.
        """
        return self.int("MAIL_PORT", default=25)

    @property
    def MAIL_USE_TLS(self) -> bool:
        """Use TLS for emails.

        Default value is ``False``.
        """
        return self.bool("MAIL_USER_TLS", default=False)

    @property
    def MAIL_USE_SSL(self) -> bool:
        """Use SSL for emails.

        Default value is ``False``.
        """
        return self.bool("MAIL_USER_SSL", default=False)

    @property
    def MAIL_USERNAME(self) -> str | None:
        """Username for mail server.

        Default value is ``None``.
        """
        return self.str("MAIL_USERNAME", default=None)

    @property
    def MAIL_PASSWORD(self) -> str | None:
        """Password for mail server.

        Default value is ``None``.
        """
        return self.str("MAIL_PASSWORD", default=None)

    @property
    def POSTS_PER_PAGE(self) -> int:
        """Posts to paginate per page.

        Default value is ``25``.
        """
        return self.int("POSTS_PER_PAGE", default=25)

    @property
    def RESERVED_USERNAMES(self) -> list[str]:
        """List of names that cannot be registered.

        Default value is ``[]``.
        """
        return self.list("RESERVED_USERNAMES", default=[])

    @property
    def BRAND(self) -> str:
        """App branding to display on navbar and browser tabs.

        Default value is ``""``.
        """
        return self.str("BRAND", default="")

    @property
    def COPYRIGHT(self) -> str:
        """Return the copyright line from LICENSE else None."""
        return self.str(
            "COPYRIGHT",
            default=(self._root_path.parent / "LICENSE")
            .read_text(encoding="utf-8")
            .splitlines()[2],
        )

    @property
    def COPYRIGHT_YEAR(self) -> str:
        """Year the copyright is valid for.

        By default this will be parsed from the LICENSE of this
        repository.
        """
        return self.str("COPYRIGHT_YEAR", default=self.COPYRIGHT.split()[2])

    @property
    def COPYRIGHT_AUTHOR(self) -> str:
        """Copyright holder of the application.

        By default this will be parsed from the LICENSE of this
        repository.
        """
        return self.str(
            "COPYRIGHT_AUTHOR", default=" ".join(self.COPYRIGHT.split()[3:])
        )

    @property
    def COPYRIGHT_EMAIL(self) -> str:
        """Copyright holder's email.

        By default this will be parsed from the pyproject.toml of this
        repository.
        """
        return self.str(
            "COPYRIGHT_EMAIL",
            default=tomli.loads(
                (self._root_path.parent / "pyproject.toml").read_text()
            )
            .get("tool", {})
            .get("poetry", {})
            .get("authors", [])[0]
            .split()[1][1:-1],
        )

    @property
    def NAVBAR_HOME(self) -> bool:
        """Include ``Home`` in navbar as opposed to only the brand.

        Default value is ``True``.
        """
        return self.bool("NAVBAR_HOME", default=True)

    @property
    def NAVBAR_ICONS(self) -> bool:
        """Display certain links in navbar as icons instead of text.

        Default value is ``False``.
        """
        return self.bool("NAVBAR_ICONS", default=False)

    @property
    def NAVBAR_USER_DROPDOWN(self) -> bool:
        """Display logged-in user links as dropdown.

        Default value is ``False``.
        """
        return self.bool("NAVBAR_USER_DROPDOWN", default=False)

    @property
    def SESSION_COOKIE_HTTPONLY(self) -> bool:
        """Don't allow JavaScript access to marked cookies.

        Default value is ``True``.
        """
        return self.bool("SESSION_COOKIE_HTTPONLY", default=True)

    @property
    def SESSION_COOKIE_SECURE(self) -> bool:
        """Only send cookies with requests over HTTPS.

        If the cookie is marked "secure" the application must be served
        over HTTPS for this to make sense.

        Default value is ``True``.
        """
        return self.bool("SESSION_COOKIE_SECURE", default=True)

    @property
    def SESSION_COOKIE_SAMESITE(self) -> str:
        """Restrict how cookies are sent with external requests.

        Default value is ``"strict"``.
        """
        return self.str("REMEMBER_COOKIE_SAMESITE", default="strict")

    @property
    def REMEMBER_COOKIE_SECURE(self) -> bool:
        """Set remember-cookie secure parameter.

        The cookie for the ``Remember Me`` checkbox in logins.

        Default value is ``True``.
        """
        return self.bool("REMEMBER_COOKIE_SECURE", default=True)

    @property
    def PREFERRED_URL_SCHEME(self) -> str:
        """Whether HTTP or HTTPS is preferred.

        Default value is ``https``.
        """
        return self.str("PREFERRED_URL_SCHEME", default="https")

    @property
    def CSP(self) -> dict[str, str | list[str]]:
        """Policies to add to existing `Content Security Policy`_.

        .. _Content Security Policy:
            https://github.com/jshwi/jss/blob/master/app/schemas/
            csp.json

        Default value is ``{}``.
        """
        return self.dict("CSP", default={})

    @property
    def CSP_REPORT_ONLY(self) -> bool:
        """Do not enforce CSP and only report violations.

        Default value is ``True``.
        """
        return self.bool("CSP_REPORT_ONLY", default=True)

    @property
    def BOOTSTRAP_SERVE_LOCAL(self) -> bool:
        """Bootstrap resources will be served from the local app.

        See `CDN support`_ for details.

        .. _CDN support:
            https://pythonhosted.org/Flask-Bootstrap/cdn.html

        Default value is ``True``.
        """
        return self.bool("BOOTSTRAP_SERVE_LOCAL", default=True)

    @property
    def SIGNATURE(self) -> str:
        """Signature to sign emails off with.

        Default value is ``BRAND``.
        """
        return self.str("SIGNATURE", default=self.BRAND)

    @property
    def ADMIN_SECRET(self) -> str:
        """Password for initialized admin user.

        Default value is ``None``.
        """
        return self.str("ADMIN_SECRET", default=None)

    @property
    def TRANSLATIONS_DIR(self) -> Path:
        """Path to translation files.

        Default value is ``app.root_path / "translations"``.
        """
        return self.path(
            "TRANSLATIONS_DIR", default=self._root_path / "translations"
        )

    @property
    def LANGUAGES(self) -> list[str]:
        """Supported languages.

        Default value is ``["en"]``.
        """
        return self.list(
            "LANGUAGES",
            default=["es"] + [p.name for p in self.TRANSLATIONS_DIR.iterdir()],
        )

    @property
    def SHOW_POSTS(self) -> bool:
        """Show posts from database.

        Default value is ``True``.
        """
        return self.bool("SHOW_POSTS", default=True)

    @property
    def TITLE(self) -> str:
        """Header for page.

        Default value is ``""``.
        """
        return self.str("TITLE", default="")

    @property
    def SHOW_REGISTER(self) -> bool:
        """Show ``Register`` option in navbar.

        Default value is ``True``.
        """
        return self.bool("SHOW_REGISTER", default=True)

    @property
    def SHOW_PAYMENT(self) -> bool:
        """Show payment option.

        Default value is ``False``.
        """
        return self.bool("SHOW_PAYMENT", default=False)

    @property
    def STRIPE_SECRET_KEY(self) -> str:
        """Secret key for Stripe API.

        Default value is ``None``.
        """
        return self.str("STRIPE_SECRET_KEY", default=None)

    @property
    def PAYMENT_OPTIONS(self) -> dict[str, str]:
        """Key-value pairs of payment options for Stripe's API.

        Price is in US cents.

        Default value is ``{"price": "None"}``.
        """
        return self.dict("PAYMENT_OPTIONS", default={"price": "None"})

    @property
    def MAX_CONTENT_LENGTH(self) -> int:
        """Max content length for file uploads.

        Default value is ``1048576``.
        """
        return self.int("MAX_CONTENT_LENGTH", default=1024 * 1024)

    @property
    def UPLOAD_EXTENSIONS(self) -> list[str]:
        """Extensions allowed for upload.

        Default value is
        ``[".txt", ".pdf", ".png", ".jpg", ".jpeg", ".gif"]``.
        """
        return self.list(
            "UPLOAD_EXTENSIONS",
            default=[".txt", ".pdf", ".png", ".jpg", ".jpeg", ".gif"],
        )

    @property
    def STATIC_FOLDER(self) -> Path:
        """Path to static files.

        Default value is ``app.root_path / "static"``.
        """
        return self.path("STATIC_FOLDER", default=self._root_path / "static")

    @property
    def UPLOAD_PATH(self) -> Path:
        """Path to upload file to.

        Default value is ``"${STATIC_FOLDER}/uploads"``.
        """
        return self.path("UPLOAD_PATH", default=self.STATIC_FOLDER / "uploads")

    @property
    def SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS(self) -> bool:
        """Generate list of rules without params.

        Default value is ``True``.
        """
        return self.bool("SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS", default=True)

    @property
    def SCHEMAS(self) -> Path:
        """Path to schemas.

        Default value is ``app.root_path / "schemas"``.
        """
        return self.path("SCHEMAS", default=self._root_path / "schemas")


def init_app(app: Flask) -> None:
    """Initialize config for this application.

    :param app: Application object.
    """
    config = Config(Path(app.root_path))
    config.read_env()
    app.config.from_object(config)
    app.static_folder = app.config["STATIC_FOLDER"]
