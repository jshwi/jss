"""
app.models
==========

Define app's database models.
"""
# pylint: disable=too-few-public-methods
from __future__ import annotations

from datetime import datetime
from typing import Dict

from flask_login import UserMixin
from sqlalchemy_utils import generic_repr
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db

_USER_ID = "user.id"


@generic_repr("id")
class _BaseModel(db.Model):
    __abstract__ = True

    def export(self) -> Dict[str, str]:
        """Get post attributes as a dict of str objects.

        :return: Post as dict.
        """
        return {
            k: str(v)
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        }


class User(UserMixin, _BaseModel):  # type: ignore
    """Database schema for users."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    admin = db.Column(db.Boolean, default=False)
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    confirmed = db.Column(db.Boolean, default=True)
    confirmed_on = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        """Hash and store a new user password.

        :param password: User's choice in password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Match entered password against existing password hash.

        :param password:    User's password attempt.
        :return:            Attempt matches hash: True or False.
        """
        return check_password_hash(self.password_hash, password)


class Post(_BaseModel):
    """Database schema for posts."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String)
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey(_USER_ID))
