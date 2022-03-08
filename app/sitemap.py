from app.extensions import sitemap
from datetime import datetime


def loc(x):
    yield x, {}, datetime.now(), "never", 0.7


entry = {"auth": ["register", "login", "logout", "unconfirmed"]}


def init_app():
    for entry_point in ():
        sitemap.register_generator(lambda: loc(entry_point))
