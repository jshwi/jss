"""
app.security
============
"""
from flask import Flask

from app.extensions import talisman as t
from app.utils.csp import ContentSecurityPolicy, CSPType

_SELF = "'self'"
_JSDELIVR = "cdn.jsdelivr.net"
_CLOUDFLARE = "cdnjs.cloudflare.com"
_UNSAFE_INLINE = "'unsafe-inline'"
_GRAVATAR = "gravatar.com"
_FONTS_GOOGLE_APIS = "fonts.googleapis.com"
_DATA = "data:"
_FONTS_GSTATIC = "fonts.gstatic.com"

_CSP: CSPType = {
    "default-src": [_SELF],
    "style-src": [_SELF, _UNSAFE_INLINE],
    "script-src-elem": [_SELF, _UNSAFE_INLINE, _CLOUDFLARE],
    "img-src": [_SELF, _GRAVATAR, _DATA],
    "script-src": [_SELF, _UNSAFE_INLINE],
}


def init_app(app: Flask) -> None:
    """Security config.

    :param app: Application factory object.
    """
    t.content_security_policy = ContentSecurityPolicy(_CSP)
    t.content_security_policy.update_policy(app.config["CSP"])
    t.content_security_policy_report_only = app.config["CSP_REPORT_ONLY"]
    t.content_security_policy_report_uri = app.config["CSP_REPORT_URI"]
    t.content_security_policy_nonce_in = ["style-src-attr"]
