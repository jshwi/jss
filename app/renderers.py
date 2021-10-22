"""
app.renderers
=============
"""
# pylint: disable=invalid-name,too-few-public-methods
from typing import Any, List

from dominate import tags
from dominate.tags import html_tag
from flask_bootstrap.nav import BootstrapRenderer
from flask_nav.elements import NavigationItem, Subgroup, View


class BadgedView(View):
    """``NavigationItem`` to be rendered into HTML.

    Parameters outline the rules for rendering HTML through the visitor
    pattern.

    This item will be rendered into a link to a view. The link will
    display a badge previewing the number of items that the view will
    point the user to.

    :param text: The text to display as a link and also to display
        hover-over information.
    :param count: The number to display on the link's badge. If the
        count is 0 then no badge will be rendered.
    :param badge: An instantiated ``Badge`` object which sets the
        parameters for the badged view this object constructs.
    :param endpoint: The target of the link being rendered with
        ``url_for``.
    :param kwargs: Keyword arguments to pass to ``url_for``.
    """

    def __init__(
        self,
        text: str,
        count: int,
        badge: html_tag,
        endpoint: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(text, endpoint, **kwargs)
        self.count = count
        self.badge = badge
        self.badge["class"] = "badge"


class RawUrl(View):
    """Like ``View`` only without using ``url_for``.

    Does not need a visitor method in the navbar renderer as the visitor
    class traverses the mro and this is not implemented with any
    difference to its parent class.
    """

    def get_url(self) -> str:
        """Override the parent's implementation of processing the
        endpoint and kwargs through ``url_for`` to only process a static
        url str.

        :return: The static url str passed to the constructor as
            ``endpoint.``
        """
        return self.endpoint


class ListGroup(Subgroup):
    """Register a subgroup of li items that are not part of dropdown."""


class Navbar(NavigationItem):  # pylint: disable=too-few-public-methods
    """Navbar object parameters.

    :param items: Items to place on the left side of the navbar.
    :param right_items: Items to place on the right side of the navbar.
    """

    def __init__(
        self,
        title: View,
        header: List[NavigationItem] = None,
        items: List[NavigationItem] = None,
        right_items: List[NavigationItem] = None,
    ) -> None:
        self.title = title
        self.header = header or []
        self.items = items or []
        self.right_items = right_items or []


class NavbarRenderer(BootstrapRenderer):
    """Rules for rendering the navbar HTML."""

    def visit_Navbar(  # pylint: disable=too-many-locals
        self, node: Navbar
    ) -> html_tag:
        """Render HTML via ``Bootstrap`` for navbar.

        :param node: Navbar object to add to template.
        :return: Rendered HTML.
        """
        root = tags.nav(_class="navbar navbar-default")
        cont = root.add(tags.div(_class="container"))
        header = cont.add(tags.div(_class="navbar-header"))

        # collapse button
        # this will collapse all nav items containing the ``node_id`` on
        # mobile devices
        btn = header.add(tags.button())
        btn["type"] = "button"
        btn["class"] = "navbar-toggle collapsed"
        btn["data-toggle"] = "collapse"
        btn["data-target"] = "#bs-example-navbar-collapse-1"
        btn["aria-expanded"] = "false"
        btn["aria-controls"] = "navbar"
        btn.add(tags.span("Toggle navigation", _class="sr-only"))
        btn.add(tags.span(_class="icon-bar"))  # "hamburger" menu
        btn.add(tags.span(_class="icon-bar"))
        btn.add(tags.span(_class="icon-bar"))

        # dark mode toggle
        label = header.add(tags.label(_class="switch pull-right"))
        label.add(*[self.visit(i) for i in node.header])

        # brand
        brand = header.add(tags.a(node.title.text))
        brand["class"] = "navbar-brand"
        brand["href"] = node.title.get_url()

        # div for collapsible navbar items
        # match ``node_id`` to the collapsible button defined above
        bar = cont.add(
            tags.div(
                _class="navbar-collapse collapse",
                id="bs-example-navbar-collapse-1",
            )
        )

        # navbar items
        bar_list = bar.add(tags.ul(_class="nav navbar-nav"))
        bar_list.add(*[self.visit(i) for i in node.items])

        # navbar items to the right
        right_bar_list = bar.add(tags.ul(_class="nav navbar-nav navbar-right"))
        right_bar_list.add(*[self.visit(i) for i in node.right_items])

        # return the configured <nav> element
        return root

    @staticmethod
    def visit_BadgedView(node: BadgedView) -> html_tag:
        """Render a dynamic view link, displaying a badge with count.

        :param node: A ``PreviewView`` instance.
        :return: An ``html_tag`` instance for rendering a list object
            in an unordered list.
        """
        item = tags.li()
        anchor = item.add(tags.a(node.text))
        anchor["href"] = node.get_url()
        anchor["title"] = node.text

        # create the badge that will display the number of focused items
        # if the node count is not 0
        badge = anchor.add(node.badge)
        badge["style"] = "visibility: disable"
        if node.count:
            badge["style"] = "visibility: visible"

        return item

    def visit_ListGroup(self, node: ListGroup) -> html_tag:
        """A simpler form of ``visit_Subgroup``.

        A div of list items.

        :param node: A ``ListGroup`` instance.
        :return: An ``html_tag`` instance for rendering a list object
            in an unordered list.
        """
        item = tags.li()
        div = item.add(tags.div(_class="list-group"))
        div.add(*[self.visit(i) for i in node.items])
        return item
