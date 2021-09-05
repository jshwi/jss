"""
app.config
==========

Most configuration is set via environment variables as per
https://12factor.net/config:
"""
# pylint: disable=invalid-name
from typing import List, Optional

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
    def DATABASE_URL(self) -> Optional[str]:
        """Database location."""
        return env.str("DATABASE_URL", default=None)

    @property
    def SECRET_KEY(self) -> Optional[str]:
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
    def FLASK_STATIC_DIGEST_HOST_URL(self) -> Optional[str]:
        """Set to a value such as https://cdn.example.com.

        Prefix your static path with this URL. This would be useful if
        you host your files from a CDN. Make sure to include the
        protocol (aka. https://).
        """
        return env.str("FLASK_STATIC_DIGEST_HOST_URL", default=None)

    @property
    def FLASK_STATIC_DIGEST_BLACKLIST_FILTER(self) -> List[str]:
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
    def DEFAULT_MAIL_SENDER(self) -> Optional[str]:
        """Default mail sender."""
        return env.str("DEFAULT_MAIL_SENDER", default=None)

    @property
    def MAIL_SUBJECT_PREFIX(self) -> str:
        """str object to prefix mail client's subject line with."""
        return env.str("MAIL_SUBJECT_PREFIX", default="")

    @property
    def ADMINS(self) -> Optional[List[str]]:
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


def init_app(app: Flask) -> None:
    """Register ``Config`` object.

    :param app: App object.
    """
    app.config.from_object(Config())
