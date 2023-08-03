"""
app.views.database
==================

Admin page initialized with models for reading and writing.
"""
from __future__ import annotations

from flask import Flask
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib import sqla
from flask_login import current_user, login_required
from werkzeug import Response

from app.extensions import db
from app.models import Message, Notification, Post, Task, User
from app.views.security import admin_required

_INDEX = "index"


class _MyModelView(sqla.ModelView):
    def __init__(
        self, model: db.Model, session: db.session  # type: ignore
    ) -> None:
        super().__init__(model, session)
        self.endpoint = f"{model.__table__}s"

    def is_accessible(self) -> None:
        """Only allow access if user is logged in as admin."""
        return current_user.is_authenticated and current_user.admin


class MyAdminIndexView(AdminIndexView):
    """Custom index view that handles login / registration."""

    @expose("/")
    @login_required
    @admin_required
    def index(self) -> str | Response:
        """Requires user be logged in as admin.

        :return: Admin index page.
        """
        return super().index()


def init_app(app: Flask) -> None:
    """Add models to admin view.

    Not consistent with the application factory pattern for ``Flask``
    extensions, however, the ``Admin`` object does not integrate into
    the application well as a global singleton.

    While running ``pytest``, ``Admin`` will be called multiple times
    and the following will be raised:

        ValueError: The name 'user' is already registered for a
        different blueprint. Use 'name=' to provide a unique name.

    See https://stackoverflow.com/questions/18002750

    :param app: Application factory object.
    """
    admin = Admin(
        app,
        index_view=MyAdminIndexView(endpoint="database", url="/database"),
        base_template="/database.html",
        template_mode="bootstrap4",
    )
    admin.add_view(_MyModelView(User, db.session))
    admin.add_view(_MyModelView(Post, db.session))
    admin.add_view(_MyModelView(Message, db.session))
    admin.add_view(_MyModelView(Notification, db.session))
    admin.add_view(_MyModelView(Task, db.session))
