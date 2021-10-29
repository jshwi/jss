"""
app.dom.text
============
"""
from app.utils.models import Post
from app.utils.register import RegisterContext

# reference to this module
# replace invalid dot notation for function names with underscores
# only keep the path to this module relative to the package
_REF = "_".join(__name__.split(".")[1:])

text = RegisterContext(_REF)


@text.register
def post_title(post: Post, revision: int) -> str:
    """Variable post title.

    Return result depending on whether viewing post as is or a revision
    of an edited post.

    :param post: Post ORM object.
    :param revision: Revision starting from 1.
    :return: Title as ``str``.
    """
    if revision == -1:
        return post.title

    return f"{post.title} v({revision + 1})"
