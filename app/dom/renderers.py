"""
app.html.renderers
==================
"""
# pylint: disable=invalid-name,too-few-public-methods
from hashlib import sha1
from typing import Any, List, Optional

from dominate import tags
from dominate.tags import html_tag
from flask_nav.elements import NavigationItem, Subgroup, View
from visitor import Visitor


class IconView(View):
    """View which can be set to display text or icons.

    For icons to be set to on the app needs to be configured with
    ``NAVBAR_ICONS`` set to True and an icon span class needs to be
    passed to the constructor.

    :param text: The text to display as a link and also to display
        hover-over information.
    :param endpoint: The target of the link being rendered with
        ``url_for``.
    :param kwargs: Keyword arguments to pass to ``url_for``.
    """

    def __init__(self, text: str, endpoint: str, **kwargs: str) -> None:
        super().__init__(text, endpoint, **kwargs)
        self.text = text
        self.title = text
        self.cls = "nav-link "

    def set_icon(self, icon: str) -> None:
        """Override attributes to render an icon instead of text.

        :param icon: Icon attribute.
        """
        self.text = tags.span(cls=icon)
        self.cls += "btn-lg btn-link"


class BadgedView(IconView):
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

    def set_icon(self, icon: str) -> None:
        """Override attributes to render an icon instead of text.

        :param icon: Icon attribute.
        """
        super().set_icon(icon)
        self.badge["class"] += " badge-pill badge-primary badge-notify"


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


class NavbarRenderer(Visitor):
    """Rules for rendering the navbar HTML."""

    def __init__(self, html5: bool = True, id: Optional[int] = None):
        self.html5 = html5
        self._in_dropdown = False
        self.id = id

    def visit_Navbar(  # pylint: disable=too-many-locals
        self, node: Navbar
    ) -> html_tag:
        """Render HTML via ``Bootstrap`` for navbar.

        :param node: Navbar object to add to template.
        :return: Rendered HTML.
        """
        node_id = sha1(str(id(node)).encode()).hexdigest()
        nav = tags.nav(cls="navbar navbar-expand-lg navbar-light bg-light")

        a = nav.add(tags.a(cls="navbar-brand", href=node.title.get_url()))
        a.add(node.title.text)

        ul_right = nav.add(tags.ul(cls="navbar-nav ml-auto navbar-right"))

        toggle_dark_mode = ul_right.add(
            tags.input_(
                id="toggle-darkreader",
                type="checkbox",
                data_toggle="toggle",
                data_onstyle="outline-dark",
                data_offstyle="outline-light",
                data_style="border",
                data_on="<i class='bi bi-sun'></i>",
                data_off="<i class='bi-moon'></i>",
                onchange="toggleDarkReader()",
            )
        )
        toggle_dark_mode.add("toggle-darkreader")

        collapse_button = nav.add(
            tags.button(
                cls="navbar-toggler",
                type="button",
                data_toggle="collapse",
                data_target=f"#{node_id}",
                aria_controls="navbarSupported",
                aria_expanded="false",
                aria_label="Toggle navigation",
            )
        )
        collapse_button.add(
            tags.span("Toggle navigation", cls="sr-only"),
            tags.span(cls="navbar-toggler-icon"),
        )

        collapsible_div = nav.add(
            tags.div(cls="collapse navbar-collapse", id=node_id)
        )

        collapsible_ul = collapsible_div.add(tags.ul(cls="navbar-nav mr-auto"))
        collapsible_ul.add(*[self.visit(i) for i in node.items])

        # navbar items to the right
        collapsible_ul_right = collapsible_div.add(
            tags.ul(cls="nav navbar-nav ml-auto")
        )
        collapsible_ul_right.add(*[self.visit(i) for i in node.right_items])

        # return the configured <nav> element
        return nav

    @staticmethod
    def visit_BadgedView(node: BadgedView) -> html_tag:
        """Render a dynamic view link, displaying a badge with count.

        :param node: A ``PreviewView`` instance.
        :return: An ``html_tag`` instance for rendering a list object
            in an unordered list.
        """
        li = tags.li(cls="nav-item")
        a = li.add(tags.a(cls=node.cls, href=node.get_url(), title=node.title))
        a.add(node.text)

        # create the badge that will display the number of focused items
        # if the node count is not 0
        if node.count:
            a.add(node.badge)

        return li

    def visit_ListGroup(self, node: ListGroup) -> html_tag:
        """A simpler form of ``visit_Subgroup``.

        A div of list items.

        :param node: A ``ListGroup`` instance.
        :return: An ``html_tag`` instance for rendering a list object
            in an unordered list.
        """
        li = tags.li(cls="nav-item")
        div = li.add(tags.div(cls="list-group"))
        div.add(*[self.visit(i) for i in node.items])
        return li

    @staticmethod
    def visit_IconView(node: IconView) -> html_tag:
        """Render a view which can also be set to display icons.

        :param node: The ``IconView`` instance.
        :return: An ``html_tag`` instance for rendering a list object
            in an unordered list.
        """
        li = tags.li(cls="nav-item")
        a = li.add(tags.a(cls=node.cls, href=node.get_url(), title=node.title))
        a.add(node.text)
        return li

    # all the below is from `Flask-Bootstrap.nav.BootstrapRenderer`
    # cannot be installed at the same time as `Bootstrap-Flask`
    # in order to avoid to many changes between migration, hard code
    # this instead of importing

    def visit_Subgroup(self, node: Subgroup) -> html_tag:
        """Render a subgroup.

        :return: An ``html_tag`` instance for rendering a subgroup.
        """
        li = tags.li(cls="nav-item")
        if not self._in_dropdown:
            a = li.add(
                tags.a(
                    href="#",
                    cls="nav-link dropdown-toggle",
                    data_toggle="dropdown",
                    role="button",
                    aria_haspopup="true",
                    aria_expanded="false",
                )
            )
            a.add(node.title, tags.span(cls="caret"))

            ul = li.add(tags.ul(cls="dropdown-menu dropdown-menu-right"))
            self._in_dropdown = True
            for item in node.items:
                ul.add(self.visit(item))

            self._in_dropdown = False

        return li

    @staticmethod
    def visit_View(node: View) -> html_tag:
        """Render a view.

        :return: An ``html_tag`` instance for rendering a view.
        """
        li = tags.li(cls="nav-item", href=node.get_url(), title=node.text)
        a = li.add(tags.a(cls="nav-link", href=node.get_url()))
        a.add(node.text)
        if node.active:
            li["class"] = "nav-item active"

        return li
