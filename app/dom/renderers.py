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
        self.cls = ""

    def set_icon(self, icon: str) -> None:
        """Override attributes to render an icon instead of text.

        :param icon: Icon attribute.
        """
        self.text = tags.span(cls=icon)
        self.cls = "btn-lg btn-link"


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
        self.badge["class"] += " icon-badge-notify"


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


class Toggler(NavigationItem):
    """Toggle input item.

    :param text: The text to display as a link and also to display
        hover-over information.
    :param kwargs: Parameters to pass to the input tag.
    """

    def __init__(self, text: str, **kwargs) -> None:
        self.text = text
        self.kwargs = kwargs


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
        nav = tags.nav(cls="navbar navbar-default")
        container = nav.add(tags.div(cls="container-fluid"))

        # header; div2
        div_header = container.add(tags.div(cls="navbar-header"))
        collapse_button = div_header.add(
            tags.button(
                type="button",
                cls="navbar-toggle collapsed",
                data_toggle="collapse",
                data_target=f"#{node_id}",
                aria_expanded="false",
                aria_controls="navbar",
            )
        )
        collapse_button.add(
            tags.span("Toggle navigation", cls="sr-only"),
            tags.span(cls="icon-bar"),  # "hamburger" menu
            tags.span(cls="icon-bar"),
            tags.span(cls="icon-bar"),
        )

        label = div_header.add(tags.label(cls="switch pull-right"))
        label.add(*[self.visit(i) for i in node.header])

        a = div_header.add(
            tags.a(cls="navbar-brand", href=node.title.get_url())
        )
        a.add(node.title.text)

        collapsible_div = container.add(
            tags.div(cls="navbar-collapse collapse", id=node_id)
        )

        ul = collapsible_div.add(tags.ul(cls="nav navbar-nav"))
        ul.add(*[self.visit(i) for i in node.items])

        # navbar items to the right
        ul_right = collapsible_div.add(
            tags.ul(cls="nav navbar-nav navbar-right")
        )
        ul_right.add(*[self.visit(i) for i in node.right_items])

        # return the configured <nav> element
        return nav

    @staticmethod
    def visit_BadgedView(node: BadgedView) -> html_tag:
        """Render a dynamic view link, displaying a badge with count.

        :param node: A ``PreviewView`` instance.
        :return: An ``html_tag`` instance for rendering a list object
            in an unordered list.
        """
        li = tags.li()
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
        li = tags.li()
        div = li.add(tags.div(cls="list-group"))
        div.add(*[self.visit(i) for i in node.items])
        return li

    @staticmethod
    def visit_Toggler(node: Toggler) -> html_tag:
        """Render a toggle input item.

        :param node: A ``Toggler`` instance.
        :return: An ``html_tag`` instance for rendering input item.
        """
        return tags.input_(node.text, **node.kwargs)

    @staticmethod
    def visit_IconView(node: IconView) -> html_tag:
        """Render a view which can also be set to display icons.

        :param node: The ``IconView`` instance.
        :return: An ``html_tag`` instance for rendering a list object
            in an unordered list.
        """
        li = tags.li()
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
        li = tags.li(cls="dropdown")
        if not self._in_dropdown:
            a = li.add(
                tags.a(
                    href="#",
                    cls="dropdown-toggle",
                    data_toggle="dropdown",
                    role="button",
                    aria_haspopup="true",
                    aria_expanded="false",
                )
            )
            a.add(node.title, tags.span(cls="caret"))

            ul = li.add(tags.ul(cls="dropdown-menu"))
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
        li = tags.li()
        a = li.add(tags.a(href=node.get_url(), title=node.text))
        a.add(node.text)
        if node.active:
            li["class"] = "active"

        return li
