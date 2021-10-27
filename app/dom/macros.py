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
from typing import List

from dominate import tags
from dominate.tags import html_tag
from flask import url_for
from markupsafe import Markup

from app.utils.models import Post
from app.utils.register import RegisterContext

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
