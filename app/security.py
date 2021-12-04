"""
app.security
============
"""
from flask import Flask

from app.extensions import talisman as t
from app.utils.csp import ContentSecurityPolicy, CSPType

_CSP: CSPType = {
    "default-src": ["'self'", "cdn.jsdelivr.net"],
    "style-src-elem": [
        "'self'",
        "cdnjs.cloudflare.com",
        "cdn.jsdelivr.net",
        "fonts.googleapis.com",
        "'unsafe-inline'",
    ],
    "script-src-elem": [
        "'self'",
        "cdnjs.cloudflare.com",
        "cdn.jsdelivr.net",
        "'unsafe-inline'",
    ],
    "img-src": ["'self'", "gravatar.com", "data:"],
    "font-src": [
        "'self'",
        "cdnjs.cloudflare.com",
        "cdn.jsdelivr.net",
        "fonts.gstatic.com",
    ],
    "script-src-attr": ["'self'", "'unsafe-inline'"],
    "connect-src": ["'self'", "fonts.googleapis.com", "cdn.jsdelivr.net"],
}


def init_app(app: Flask) -> None:
    """Security config.

    :param app: Application factory object.
    """
    t.content_security_policy = ContentSecurityPolicy(_CSP)
    t.content_security_policy.update_policy(app.config["CSP"])
    t.content_security_policy_report_only = app.config["CSP_REPORT_ONLY"]
    t.content_security_policy_report_uri = app.config["CSP_REPORT_URI"]
