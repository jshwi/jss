"""
app.extensions.talisman
=======================
"""

from __future__ import annotations

import json
import typing as t
from pathlib import Path

from flask import Flask
from flask_talisman import (
    DEFAULT_CSP_POLICY,
    DEFAULT_DOCUMENT_POLICY,
    DEFAULT_FEATURE_POLICY,
    DEFAULT_PERMISSIONS_POLICY,
    SAMEORIGIN,
)
from flask_talisman import Talisman as _Talisman
from flask_talisman.talisman import (
    DEFAULT_REFERRER_POLICY,
    DEFAULT_SESSION_COOKIE_SAMESITE,
    ONE_YEAR_IN_SECS,
)


class ContentSecurityPolicy(t.Dict[str, t.Union[str, t.List[str]]]):
    """Object for setting default CSP and config override.

    :param schemas: Path to schemas directory.
    """

    def __init__(self, schemas: Path) -> None:
        super().__init__(
            json.loads((schemas / "csp.json").read_text(encoding="utf-8"))
        )

    def _format_value(
        self, key: str, theirs: str | list[str]
    ) -> str | list[str]:
        # start with a list, to combine "ours" and "theirs"
        value = []
        ours = self.get(key)

        # loop through both to determine the types of each
        for item in theirs, ours:
            # if one of the items is a list concatenate it to the list
            # we are constructing
            if isinstance(item, list):
                value += item

            # if one of the items is a str append it to the list we are
            # constructing
            elif isinstance(item, str):
                value.append(item)

        # remove duplicates by converting the list to a set and then
        # back to a list again
        # for consistency and testing ensure the list is in
        # alphabetical / numerical order
        value = sorted(list(set(value)))

        # if there is only one item left after removing duplicates then
        # it can be the only item returned
        if len(value) == 1:
            return value[0]

        return value

    def update_policy(self, update: ContentSecurityPolicy) -> None:
        """Combine a configured policy without overriding the existing.

        If the result is a single item, add a ``str``.

        If the result is a ``list``, remove duplicates and sort.

        If either is a ``str`` and the other is a ``list``, add the
        ``str`` and the ``list`` contents to the new ``list``.

        If both are ``str`` values add to the new ``list``.

        :param update: A ``str`` or a ``list`` of ``str`` objects.
        """
        for key, value in update.items():
            self[key] = self._format_value(key, value)


class Talisman(_Talisman):  # pylint: disable=too-few-public-methods
    """Subclass ``flask_talisman.Talisman``.

    With this the ``Talisman.init_app`` can be tweaked so that
    everything remains encapsulated in the application factory, with no
    need to add additional functions to the application..
    """

    # pylint: disable=dangerous-default-value,too-many-arguments
    # pylint: disable=too-many-locals,too-many-positional-arguments
    def init_app(
        self,
        app: Flask,
        feature_policy: str | dict[str, str] = DEFAULT_FEATURE_POLICY,
        permissions_policy: str | dict[str, str] = DEFAULT_PERMISSIONS_POLICY,
        document_policy: str | dict[str, str] = DEFAULT_DOCUMENT_POLICY,
        force_https: bool = True,
        force_https_permanent: bool = False,
        force_file_save: bool = False,
        frame_options: str = SAMEORIGIN,
        frame_options_allow_from: str | None = None,
        strict_transport_security: bool = True,
        strict_transport_security_preload: bool = False,
        strict_transport_security_max_age: int = ONE_YEAR_IN_SECS,
        strict_transport_security_include_subdomains: bool = True,
        content_security_policy: str | dict[str, str] = DEFAULT_CSP_POLICY,
        content_security_policy_report_uri: str | None = None,
        content_security_policy_report_only: bool = False,
        content_security_policy_nonce_in: list[str] | None = None,
        referrer_policy: str = DEFAULT_REFERRER_POLICY,
        session_cookie_secure: bool = True,
        session_cookie_http_only: bool = True,
        session_cookie_samesite: str = DEFAULT_SESSION_COOKIE_SAMESITE,
        x_content_type_options: bool = True,
        x_xss_protection: bool = True,
    ) -> None:
        """Set up this instance for use with app."""
        csp = ContentSecurityPolicy(app.config["SCHEMAS"])
        csp.update_policy(app.config["CSP"])
        super().init_app(
            app,
            feature_policy=feature_policy,
            permissions_policy=permissions_policy,
            document_policy=document_policy,
            force_https=force_https,
            force_https_permanent=force_https_permanent,
            force_file_save=force_file_save,
            frame_options=frame_options,
            frame_options_allow_from=frame_options_allow_from,
            strict_transport_security=strict_transport_security,
            strict_transport_security_preload=(
                strict_transport_security_preload
            ),
            strict_transport_security_max_age=(
                strict_transport_security_max_age
            ),
            strict_transport_security_include_subdomains=(
                strict_transport_security_include_subdomains
            ),
            content_security_policy=csp,
            content_security_policy_report_uri="/report/csp_violations",
            content_security_policy_report_only=app.config["CSP_REPORT_ONLY"],
            content_security_policy_nonce_in=["style-src-attr"],
            referrer_policy=referrer_policy,
            session_cookie_secure=session_cookie_secure,
            session_cookie_http_only=session_cookie_http_only,
            session_cookie_samesite=session_cookie_samesite,
            x_content_type_options=x_content_type_options,
            x_xss_protection=x_xss_protection,
        )
