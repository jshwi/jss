"""
app.utils.tasks
===============

Setup app's background task functionality.
"""
import json
import sys
import time

from flask import render_template
from rq import get_current_job

from app import create_app
from app.models import Post, Task, User, db
from app.utils.mail import send_email

_app = create_app()

_app.app_context().push()


def _set_task_progress(progress: int) -> None:
    # set the percentage of a task's progress
    # mark task as complete when 100 reached
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notifications(
            "task_progress", {"task_id": job.get_id(), "progress": progress}
        )
        if progress >= 100:
            task.complete = True

        db.session.commit()


def export_posts(user_id: int) -> None:
    """Export user's posts to JSON and then email them.

    :param user_id: ID of user to email their posts to.
    """
    # noinspection PyBroadException
    try:
        data = []
        _set_task_progress(0)
        user = User.query.get(user_id)

        # get all user's posts (the oldest first)
        # noinspection PyUnresolvedReferences
        posts = user.posts.order_by(Post.created.asc())
        total = posts.count()
        for count, post in enumerate(posts, 1):
            data.append(post.export())
            _set_task_progress(100 * count // total)
            time.sleep(5)

        send_email(
            subject=f"Posts by {user.username}",
            recipients=[user.email],
            html=render_template(
                "email/export_posts.html", username=user.username
            ),
            attachments=[
                dict(
                    filename="posts.json",
                    content_type="application/json",
                    data=json.dumps({"posts": data}, indent=4, sort_keys=True),
                )
            ],
            sync=True,
        )

    except Exception:  # pylint: disable=broad-except
        # come back to this once you know what errors need excepting
        # all exceptions need to be caught to prevent the app from
        # crashing entirely, and clean-up still needs to be done with
        # `finally`
        _app.logger.error(  # pylint: disable=no-member
            "Unhandled exception", exc_info=sys.exc_info()
        )
    finally:
        _set_task_progress(100)
