"""
app.admin
=========

Admin page initialized with models for reading and writing.
"""
from flask import Flask
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib import sqla
from flask_login import current_user, login_required

from .extensions import db
from .models import Message, Notification, Post, Task, User
from .security import admin_required

_INDEX = "index"


class MyModelView(sqla.ModelView):
    """Custom model view that determines accessibility."""

    def is_accessible(self) -> None:
        """Only allow access if user is logged in as admin."""
        return current_user.is_authenticated and current_user.admin


class MyAdminIndexView(AdminIndexView):
    """Custom index view that handles login / registration."""

    @expose("/")
    @login_required
    @admin_required
    def index(self) -> str:
        """Requires user be logged in as admin."""
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
        index_view=MyAdminIndexView(),
        base_template="/admin/master.html",
        template_mode="bootstrap4",
    )
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Post, db.session))
    admin.add_view(MyModelView(Message, db.session))
    admin.add_view(MyModelView(Notification, db.session))
    admin.add_view(MyModelView(Task, db.session))
