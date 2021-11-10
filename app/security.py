"""
app.security
============
"""
from flask import Flask

from app.extensions import talisman as t
from app.utils.csp import ContentSecurityPolicy


def init_app(app: Flask) -> None:
    """Security config.

    :param app: Application factory object.
    """
    t.content_security_policy = ContentSecurityPolicy()
    t.content_security_policy.update_policy(app.config["CSP"])
    t.content_security_policy_report_only = app.config["CSP_REPORT_ONLY"]
    t.content_security_policy_report_uri = app.config["CSP_REPORT_URI"]
