"""
app.security
============
"""
from flask import Flask

from app.extensions import talisman as t
from app.utils.csp import ContentSecurityPolicy, CSPType

_CSP: CSPType = {
    "default-src": ["'self'"],
    "style-src-elem": ["'self'", "cdnjs.cloudflare.com", "cdn.jsdelivr.net"],
    "script-src-elem": ["'self'", "cdnjs.cloudflare.com", "cdn.jsdelivr.net"],
    "img-src": ["'self'", "gravatar.com"],
    "font-src": ["'self'", "cdnjs.cloudflare.com", "cdn.jsdelivr.net"],
}


def init_app(app: Flask) -> None:
    """Security config.

    :param app: Application factory object.
    """
    t.content_security_policy = ContentSecurityPolicy(_CSP)
    t.content_security_policy.update_policy(app.config["CSP"])
    t.content_security_policy_report_only = app.config["CSP_REPORT_ONLY"]
    t.content_security_policy_report_uri = app.config["CSP_REPORT_URI"]
