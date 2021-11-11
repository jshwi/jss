"""
app.html.macros
===============

More complex logic written here and not in ``Jinja.`` This makes it
easier to run unittests.

Functions will return ``html_tags`` and not rendered ``Markup``. This
ensures all functions can share tags with each other. When functions
are registered into context processor they will be wrapped with
``Markup``.
"""
# pylint: disable=invalid-name
from datetime import datetime
from typing import List, Optional, Union

from dominate import tags
from dominate.tags import html_tag
from flask import get_flashed_messages, url_for
from flask_login import current_user
from markupsafe import Markup

from app.extensions import markdown
from app.utils.models import Message, Post
from app.utils.register import RegisterContext

DATETIME_FMT = "h:mmA DD/MM/YYYY"

# reference to this module
# replace invalid dot notation for function names with underscores
# only keep the path to this module relative to the package
_REF = "_".join(__name__.split(".")[1:])

macros = RegisterContext(_REF, Markup)


@macros.register
def moment(timestamp: datetime) -> html_tag:
    """Render timestamps with ``moment.js``.

    :param timestamp: ``datetime`` object.
    :return: ``<span>...</span>`` containing ``moment.js`` timestamp.
    """
    return tags.span(
        cls="flask-moment",
        data_format=DATETIME_FMT,
        data_function="format",
        data_refresh="0",
        data_timestamp=str(timestamp),
    )


@macros.register
def version_dropdown(post: Post) -> html_tag:
    """Render an HTML dropdown based on the versions of posts available.

    :param post: Post ORM object of posts with version history.
    :return: ``<div>...</div>`` dropdown as ``html_tag`` object.
    """
    versions: List[Post] = post.versions.all()
    div = tags.div(
        tags.a(
            "Versions",
            tags.span(cls="caret"),
            href="#",
            cls="dropdown-toggle",
            data_toggle="dropdown",
        ),
        cls="dropdown",
    )
    ul = div.add(tags.ul(cls="dropdown-menu", role="menu"))

    # populate <ul>...</ul>
    for count, _ in enumerate(versions):

        # version id should begin at 1...
        version_id = count + 1
        li = ul.add(tags.li())

        # ...but we are still getting the# version via its list index
        a = li.add(
            tags.a(href=url_for("post.read", id=post.id, revision=count))
        )

        if version_id == len(versions):
            # the last version is the current version
            a.add(f"v{version_id}: This revision")
            a["style"] = "pointer-events: none"
        elif version_id == len(versions) - 1:
            # the version before the current version is highlighted for
            # easy rollback
            a.add(f"v{version_id}: Previous revision")
        else:
            # all other versions
            a.add(f"v{version_id}")

    return div


@macros.register
def flash_messages() -> html_tag:
    """Render flashed messages.

    :return: Flashed messages within``<div>...</div>`` as ``html_tag``
        object.
    """
    div = tags.div()
    for message in get_flashed_messages():
        div.add(tags.div(message, cls="alert alert-info", role="alert"))

    return div


@macros.register
def task_progress() -> html_tag:
    """Display a tasks progress as its percentage through progress bar.

    :return: Task progress display as percentage within
        ``<div>...</div>`` ``html_tag`` object.
    """
    div = tags.div()
    if current_user.is_authenticated:
        for task in current_user.get_tasks_in_progress():
            div.add(
                tags.div(
                    task.description,
                    tags.span(task.get_progress(), id=f"{task.id}-progress"),
                    cls="alert alert-success",
                )
            )

    return div


@macros.register
def read_posts(posts: Union[Post, Message]) -> html_tag:
    """Display posts depending on what post collection is provided.

    :param posts: Post ORM object.
    :return: Posts within ``<div>...</div>`` ``html_tag`` object.
    """
    div = tags.div()
    for post in posts.items:

        # link to profile of the user who created the current iteration
        # of posts
        profile_url = url_for("public.profile", username=post.author.username)

        # this will group each individual post, visibly separated by a
        # horizontal rule
        # table will be separated by a left section with user
        # information and a right section displaying the post
        table, _ = div.add(tags.table(cls="table table-hover"), tags.tr())

        # user information
        left_td = table.add(tags.td(cls="user-post-td"))
        left_td.add(
            # user's avatar linked to their profile
            tags.a(
                tags.img(src=post.author.avatar(70), img=post.author.username),
                href=profile_url,
            ),
            # user's bio
            tags.div(
                tags.a(post.author.username, href=profile_url),
                tags.br(),
                moment(post.created),
                cls="about",
            ),
        )

        # display post
        right_td = table.add(tags.td())
        h1 = right_td.add(tags.h1())

        # post title linked to the post's full page
        a = h1.add(tags.a(href=url_for("post.read", id=post.id)))

        # variable data depending on whether the ``Post/Message``
        # object is a ``Post`` object and not a ``Message`` object
        if isinstance(post, Post):

            # variable data depending on whether the user profile loaded
            # is of a user profile being viewed by another user or a
            # user profile being viewed by that user
            a.add(post.title)
            if (
                current_user.is_authenticated
                and current_user.id == post.user_id
            ):

                # a ``Post`` can be edited by the user who created it
                left_td.add(
                    tags.a(
                        "Edit",
                        cls="action",
                        href=url_for("post.update", id=post.id),
                    )
                )

                # if the length of versions is more than 1 (1 being the
                # initial version) then there are other versions that
                # can be reviewed with the dropdown
                if post.versions.count() > 1:
                    left_td.add(version_dropdown(post))

        # display the post content as rendered markdown html
        right_td.add(tags.div(markdown.render(post.body)))

    return div


@macros.register
def post_footer_nav(
    prev_url: Optional[str], next_url: Optional[str]
) -> html_tag:
    """Bottom navbar for newer and older post navigation.

    :param prev_url: URL to previous posts.
    :param next_url: URL to next posts.
    :return: Navbar as ``html_tag`` object.
    """
    nav = tags.nav(aria_label="...")
    ul = nav.add(tags.ul(cls="pager"))

    # newer posts
    li = ul.add(tags.li())
    a = li.add(tags.a("Newer posts"))
    if prev_url is not None:
        li["class"] = "previous"
        a["href"] = prev_url
    else:
        li["class"] = "previous disabled"
        a["href"] = "#"

    # older posts
    li = ul.add(tags.li())
    a = li.add(tags.a("Older posts"))
    if next_url is not None:
        li["class"] = "next"
        a["href"] = next_url
    else:
        li["class"] = "next disabled"
        a["href"] = "#"

    return nav


@macros.register
def post_times(post: Post) -> html_tag:
    """Display time user created post.

    If user has edited their post show the timestamp for that as well.

    :param post: Post ORM object.
    :return: Rendered paragraph tag with post's timestamp information.
    """
    p = tags.p("Posted: ", moment(post.created), cls="small")
    if post.edited is not None:
        p.add(tags.br(), "Edited: ", moment(post.edited))

    return p
