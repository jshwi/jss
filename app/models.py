"""
app.models
==========

Define app's database models.
"""
# pylint: disable=too-few-public-methods
from __future__ import annotations

import json
from datetime import datetime
from hashlib import md5
from time import time
from typing import Any, Dict, List, Optional

from flask import current_app
from flask_login import UserMixin
from flask_sqlalchemy import BaseQuery
from redis import RedisError
from rq.exceptions import NoSuchJobError
from rq.job import Job
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy_utils import generic_repr
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db

_USER_ID = "user.id"

followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey(_USER_ID)),
    db.Column("followed_id", db.Integer, db.ForeignKey(_USER_ID)),
)


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
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed: RelationshipProperty = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic",
    )
    messages_sent = db.relationship(
        "Message",
        foreign_keys="Message.sender_id",
        backref="author",
        lazy="dynamic",
    )
    messages_received = db.relationship(
        "Message",
        foreign_keys="Message.recipient_id",
        backref="recipient",
        lazy="dynamic",
    )
    last_message_read_time = db.Column(db.DateTime)
    notifications = db.relationship(
        "Notification", backref="user", lazy="dynamic"
    )
    tasks = db.relationship("Task", backref="user", lazy="dynamic")

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

    def avatar(self, size: int) -> str:
        """Generate unique avatar for user derived from email hash.

        :param size:    Size of the avatar.
        :return:        URL leading to avatar for img link.
        """
        digest = md5(self.email.lower().encode()).hexdigest()
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

        :param user:    User model object of user to check if following.
        :return:        Following the user? True or False.
        """
        return (
            self.followed.filter(followers.c.followed_id == user.id).count()
            > 0
        )

    def followed_posts(self) -> List[Post]:
        """Get all posts that the user is following.

        :return:    List of posts that the user is following in
                    descending order.
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

    def add_notifications(self, name: str, data: Any) -> Notification:
        """Add user's notifications to database.

        :param name:    Name of the database key.
        :param data:    Saved data.
        :return:        Instantiated ``Notification`` database model.
        """
        self.notifications.filter_by(name=name).delete()

        # `user` is a backref for `Task` and not defined as a column
        notification = Notification(name=name, user=self)  # type: ignore
        notification.set_mapping(data)
        db.session.commit()
        return notification

    def launch_task(
        self, name: str, description: str, *args: Any, **kwargs: Any
    ) -> Task:
        """Launch a user triggered task.

        :param name:        Name of the task.
        :param description: Friendly description of task.
        :param args:        Misc positional arguments to pass to `Task`.
        :param kwargs:      Misc keyword arguments to pass to `Task`.
        :return:            Instantiated `Task` object.
        """
        rq_job = current_app.task_queue.enqueue(  # type: ignore
            f"app.tasks.{name}", self.id, *args, **kwargs
        )
        task = Task(
            id=rq_job.get_id(),
            name=name,
            description=description,
            # `user` is a backref and not defined as a column
            user=self,  # type: ignore
        )
        db.session.add(task)
        return task

    def get_tasks_in_progress(self) -> List[BaseQuery]:
        """Get the currently running tasks triggered by user.

        :return:    List of ``BaseQuery`` objects returned as running
                    tasks.
        """
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name: str) -> Optional[BaseQuery]:
        """Return first task currently running under this user.

        :param name:    Name of running task.
        :return:        First running task retrieved.
        """
        return Task.query.filter_by(
            name=name, user=self, complete=False
        ).first()


class Post(_BaseModel):
    """Database schema for posts."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String)
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey(_USER_ID))


class Message(_BaseModel):
    """Database schema for user messages."""

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey(_USER_ID))
    recipient_id = db.Column(db.Integer, db.ForeignKey(_USER_ID))
    body = db.Column(db.String(140))
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class Notification(_BaseModel):
    """Database schema for notifications."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.Float, index=True, default=time)
    mapping = db.Column(db.Text)

    def set_mapping(self, mapping: Dict[str, Any]) -> None:
        """Set ``dict`` object as ``str`` (JSON).

        :param mapping: Set object as str.
        """
        self.mapping = json.dumps(mapping)

    def get_mapping(self) -> Dict[str, Any]:
        """Get dict representation of JSON data.

        :return: Dict object of notification data.
        """
        return json.loads(self.mapping)


class Task(_BaseModel):
    """Database schema for background tasks."""

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey(_USER_ID))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self) -> Optional[Job]:
        """Get a ``Redis`` queued job.

        :return: RQ job if it exists, else return None.
        """
        try:
            return Job.fetch(
                self.id, connection=current_app.redis  # type: ignore
            )

        except (RedisError, NoSuchJobError):
            return None

    def get_progress(self) -> int:
        """Get progress of instantiated task.

        :return: Integer percentage. If there is no job assume 100%.
        """
        job = self.get_rq_job()
        return 100 if job is None else job.meta.get("progress", 0)
