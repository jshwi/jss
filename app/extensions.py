"""
app.extensions
==============

Each extension is initialized with ``init_app`` method.
"""
from flask import Flask
from flask_babel import Babel
from flask_bootstrap import Bootstrap4
from flask_compress import Compress
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_misaka import Misaka
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from flask_static_digest import FlaskStaticDigest
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect

debug_toolbar = DebugToolbarExtension()
static_digest = FlaskStaticDigest()
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()
csrf_protect = CSRFProtect()
markdown = Misaka(fenced_code=True)
page_down = PageDown()
bootstrap = Bootstrap4()
moment = Moment()
talisman = Talisman()
compress = Compress()
babel = Babel()


def init_app(app: Flask) -> None:
    """Register ``Flask`` extensions.

    :param app: Application factory object.
    """
    debug_toolbar.init_app(app)
    static_digest.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf_protect.init_app(app)
    markdown.init_app(app)
    page_down.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    talisman.init_app(app)
    compress.init_app(app)
    babel.init_app(app)
