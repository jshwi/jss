"""
app.models
==========

Application's database models.
"""
# pylint: disable=too-few-public-methods
from __future__ import annotations

import hashlib
import json
import typing as t
from datetime import datetime
from time import time

from flask import abort
from flask_login import UserMixin, current_user
from flask_sqlalchemy.query import Query
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.model_builder import ModelBuilder
from sqlalchemy_utils import generic_repr
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db

make_versioned(user_cls=None)

followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id")),
)


@generic_repr("id")
class BaseModel(db.Model):  # type: ignore
    """Base model for which all models in this app are derived."""

    __abstract__ = True

    def export(self) -> dict[str, str]:
        """Get database attributes as a ``dict`` of ``str``  objects.

        :return: Database as a ``dict``.
        """
        return {
            k: str(v)
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        }


class User(UserMixin, BaseModel):
    """Database schema for users."""

    #: ID of this user.
    id = db.Column(db.Integer, primary_key=True)

    #: Username of this user.
    username = db.Column(db.String(64), index=True, unique=True)

    #: Email of this user.
    email = db.Column(db.String(120), index=True, unique=True)

    #: Password hash of this user's password.
    password_hash = db.Column(db.String(128))

    #: Date that the user was created.
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    #: Whether this this user is an admin or not.
    admin = db.Column(db.Boolean, default=False)

    #: Posts that have been added by the this user.
    posts = db.relationship("Post", backref="author", lazy="dynamic")

    #: Whether this this user is confirmed or not.
    confirmed = db.Column(db.Boolean, default=False)

    #: Date that the this user was confirmed on.
    confirmed_on = db.Column(db.DateTime)

    #: About me page for the this user.
    about_me = db.Column(db.String(140))

    #: Date that the this user last logged in on.
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    #: Whether this user is authorized to make posts or not.
    authorized = db.Column(db.Boolean, default=False)

    #: User's that this user if following.
    followed: RelationshipProperty = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic",
    )

    #: Messages that this user has sent.
    messages_sent = db.relationship(
        "Message",
        foreign_keys="Message.sender_id",
        backref="author",
        lazy="dynamic",
    )

    #: Messages this user has received.
    messages_received = db.relationship(
        "Message",
        foreign_keys="Message.recipient_id",
        backref="recipient",
        lazy="dynamic",
    )

    #: The last time the user visited the messages page.
    last_message_read_time = db.Column(db.DateTime)

    #: Notifications pending for this user.
    notifications = db.relationship(
        "Notification", backref="user", lazy="dynamic"
    )

    #: Tasks associated with this user.
    tasks = db.relationship("Task", backref="user", lazy="dynamic")

    def set_password(self, password: str) -> None:
        """Hash and store a new user password.

        :param password: User's choice in password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Match entered password against existing password hash.

        :param password: User's password attempt.
        :return: Attempt matches hash: True or False.
        """
        return check_password_hash(self.password_hash, password)

    def avatar(self, size: int) -> str:
        """Generate unique avatar for user derived from email hash.

        :param size: Size of the avatar.
        :return: URL leading to avatar for img link.
        """
        digest = hashlib.new(  # type: ignore
            "md5", self.email.lower().encode(), usedforsecurity=False
        ).hexdigest()
        return f"https://gravatar.com/avatar/{digest}?d=identicon&s={size}"

    def follow(self, user: User) -> None:
        """Follow another user if not already following.

        :param user: User model object of user to follow.
        """
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user: User) -> None:
        """Unfollow another user if already following.

        :param user: User model object of user to unfollow.
        """
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user: User) -> bool:
        """Check whether following another user.

        :param user: User model object of user to check if following.
        :return: Following the user? True or False.
        """
        return (
            self.followed.filter(followers.c.followed_id == user.id).count()
            > 0
        )

    def followed_posts(self) -> list[Post]:
        """Get all posts that the user is following.

        :return: List of posts that the user is following in descending
            order.
        """
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        # noinspection PyUnresolvedReferences
        return followed.union(own).order_by(Post.created.desc())

    def new_messages(self) -> int:
        """Get the number of new (unread) messages delivered to user.

        :return: Number of new messages delivered to user.
        """
        last_read_time = self.last_message_read_time or datetime(1000, 1, 1)
        return (
            Message.query.filter_by(recipient=self)
            .filter(Message.created > last_read_time)
            .count()
        )

    def add_notifications(
        self, name: str, data: dict[str, object]
    ) -> Notification:
        """Add user's notifications to database.

        :param name: Name of the database key.
        :param data: Saved data.
        :return: Instantiated ``Notification`` database model.
        """
        self.notifications.filter_by(name=name).delete()

        # `user` is a backref for `Task` and not defined as a column
        notification = Notification(name=name, user=self)  # type: ignore
        notification.set_mapping(data)
        db.session.commit()
        return notification

    def get_tasks_in_progress(self) -> list[Query]:
        """Get the currently running tasks triggered by user.

        :return: List of ``BaseQuery`` objects returned as running
            tasks.
        """
        return Task.query.filter_by(user=self, complete=False).all()

    @classmethod
    def resolve_all_names(cls, username: str) -> User:
        """Manage retrieval of ``User`` object by their username.

        :param username: Username to search for user under.
        :raise HTTPError: Raise ``404: Not Found`` if name not resolved.
        :return: User object.
        """
        user = cls.query.filter_by(username=username).first()
        if user is None:
            # noinspection PyUnresolvedReferences
            usernames = (
                Usernames.query.filter_by(username=username)
                .order_by(Usernames.id.desc())
                .first_or_404()
            )
            return cls.query.get(usernames.user_id)

        return user


class Post(BaseModel):
    """Database schema for posts."""

    __versioned__: t.Dict[object, object] = {}

    #: ID of the user that wrote this post.
    id = db.Column(db.Integer, primary_key=True)

    #: Title of this post.
    title = db.Column(db.String, nullable=False)

    #: Body of this post.
    body = db.Column(db.String)

    #: Date that the post was created.
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    #: ID of this post.
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    #: Date that this post was last edited.
    edited = db.Column(db.DateTime, default=None)

    def get_version(self, index: int) -> ModelBuilder | None:
        """Get version of post by index.

        If no version can be returned a ``404: Not Found`` error will
        abort instead of raising an ``IndexError``.

        :param index: Index of version beginning with 0.
        :return: PostVersion object if within index range, else None.
        """
        try:
            return self.versions[index]
        except IndexError:
            return abort(404)

    @classmethod
    def get_post(
        cls, id: int, version: int | None = None, checkauthor: bool = True
    ) -> Post:
        """Get post by post's ID or abort with ``404: Not Found.``

        Standard behaviour would be to return None, so do not bypass
        silently.

        If a version number is provided find version by index. This is
        a different search to getting post by ID, as database starts at
        1, but index always starts at 0. If no version can be returned
        a ``404: Not Found`` error will abort instead of raising an
        ``IndexError``. Assign post attributes title and body to the
        yielded ``Post`` object. The ``PostVersion`` cannot be returned
        for a restore as it is a different object and will not save
        when committing database changes.

        The ``checkauthor`` argument is defined so that the function can
        be used to get a post without checking the author. This would be
        useful if we wrote a view to show an individual post on a page
        where the user doesn't matter, because they are not modifying
        the post. If the logged in author does not own the post abort
        with ``403: Forbidden``.

        :param id: The post's ID.
        :param version: If provided populate session object with
            version.
        :param checkauthor: Rule whether to check for author ID.
        :return: Post's connection object.
        """
        post = cls.query.filter_by(id=id).first_or_404()
        if version is not None:
            post_version = post.get_version(version)
            if post_version is not None:
                post.title = post_version.title
                post.body = post_version.body

        if checkauthor and post.user_id != current_user.id:
            abort(403)

        return post


class Message(BaseModel):
    """Database schema for user messages."""

    #: Message ID.
    id = db.Column(db.Integer, primary_key=True)

    #: ID of the sender of the message.
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    #: ID of the recipient of the message.
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    #: Message body.
    body = db.Column(db.String(140))

    #: Date that the message was created and sent.
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class Notification(BaseModel):
    """Database schema for notifications."""

    #: ID of this notification.
    id = db.Column(db.Integer, primary_key=True)

    #: Name of this notification.
    name = db.Column(db.String(128), index=True)

    #: ID of the user who this notification belongs to.
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    #: Date this notification was created.
    timestamp = db.Column(db.Float, index=True, default=time)

    #: Database to JSON dictionary mapping as a string.
    mapping = db.Column(db.Text)

    def set_mapping(self, mapping: dict[str, object]) -> None:
        """Set ``dict`` object as ``str`` (JSON).

        :param mapping: Set object as str.
        """
        self.mapping = json.dumps(mapping)

    def get_mapping(self) -> dict[str, object]:
        """Get dict representation of JSON data.

        :return: Dict object of notification data.
        """
        return json.loads(self.mapping)


class Task(BaseModel):
    """Database schema for background tasks."""

    #: ID of the task.
    id = db.Column(db.String(36), primary_key=True)

    #: Name of the task.
    name = db.Column(db.String(128), index=True)

    #: Description of the task.
    description = db.Column(db.String(128))

    #: User that this task belongs to.
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    #: Whether this task is complete or not.
    complete = db.Column(db.Boolean, default=False)


class Usernames(BaseModel):
    """Database schema for username changes."""

    #: ID of the username.
    id = db.Column(db.Integer, primary_key=True)

    #: Single username amongst the usernames.
    username = db.Column(db.String(64), index=True)

    #: ID of the user that this username belongs to.
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


db.configure_mappers()
