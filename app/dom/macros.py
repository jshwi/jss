"""
app.dom.macros
==============

More complex logic written here and not in ``Jinja.`` This makes it
easier to run unittests.

Functions will return ``html_tags`` and not rendered ``Markup``. This
ensures all functions can share tags with each other. When functions
are registered into context processor they will be wrapped with
``Markup``.
"""
# pylint: disable=invalid-name
from typing import List, Optional

from dominate import tags
from dominate.tags import html_tag
from flask import get_flashed_messages, url_for
from flask_login import current_user
from flask_moment import moment
from markupsafe import Markup

from app.utils.models import Post
from app.utils.register import RegisterContext

DATETIME_FMT = "h:mmA DD/MM/YYYY"

# reference to this module
# replace invalid dot notation for function names with underscores
# only keep the path to this module relative to the package
_REF = "_".join(__name__.split(".")[1:])

macros = RegisterContext(_REF, Markup)


@macros.register
def version_dropdown(post: Post) -> html_tag:
    """Render an HTML dropdown based on the versions of posts available.

    :param post: Post ORM object of posts with version history.
    :return: ``<div>...</div>`` dropdown as ``html_tag`` object.
    """
    versions: List[Post] = post.versions.all()
    div = tags.div(cls="dropdown")
    a = div.add(
        tags.a(href="#", cls="dropdown-toggle", data_toggle="dropdown")
    )
    a.add("Versions")
    a.add(tags.span(cls="caret"))
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
            a["class"] = "current-version-anchor"
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
        alert = div.add(tags.div(cls="alert alert-info", role="alert"))
        alert.add(message)

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
            alert = div.add(tags.div(cls="alert alert-success"))
            alert.add(task.description)
            span = alert.add(tags.span(id=f"{task.id}-progress"))
            span.add(task.get_progress())

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
    ul = nav.add(tags.ul(cls="pagination justify-content-center"))

    # newer posts
    li = ul.add(tags.li(cls="page-item"))
    a = li.add(tags.a(cls="page-link"))
    a.add("Previous")
    if prev_url is not None:
        a["href"] = prev_url
    else:
        li["class"] += " disabled"
        a["href"] = "#"
        a["tabindex"] = "-1"

    # older posts
    li = ul.add(tags.li(cls="page-item"))
    a = li.add(tags.a(cls="page-link"))
    a.add("Next")
    if next_url is not None:
        a["href"] = next_url
    else:
        li["class"] += " disabled"
        a["href"] = "#"
        a["tabindex"] = "-1"

    return nav


@macros.register
def post_times(post: Post) -> html_tag:
    """Display time user created post.

    If user has edited their post show the timestamp for that as well.

    :param post: Post ORM object.
    :return: Rendered paragraph tag with post's timestamp information.
    """
    p = tags.p(cls="small")
    p.add("Posted: ")
    p.add(moment(post.created).fromNow())
    if post.edited is not None:
        p.add(tags.br(), "Edited: ", moment(post.edited).fromNow())

    return p
