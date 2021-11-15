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
        self.aclass = ""

    def set_icon(self, icon: str) -> None:
        """Override attributes to render an icon instead of text.

        :param icon: Icon attribute.
        """
        self.text = tags.span(_class=icon)
        self.aclass = "btn-lg btn-link"


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
        root = tags.nav(_class="navbar navbar-default")
        cont = root.add(tags.div(_class="container-fluid"))
        header = cont.add(tags.div(_class="navbar-header"))

        # collapse button
        # this will collapse all nav items containing the ``node_id`` on
        # mobile devices
        btn = header.add(tags.button())
        btn["type"] = "button"
        btn["class"] = "navbar-toggle collapsed"
        btn["data-toggle"] = "collapse"
        btn["data-target"] = f"#{node_id}"
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
        bar = cont.add(tags.div(_class="navbar-collapse collapse", id=node_id))

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
        anchor["title"] = node.title
        anchor["href"] = node.get_url()
        anchor["class"] = node.aclass

        # create the badge that will display the number of focused items
        # if the node count is not 0
        if node.count:
            anchor.add(node.badge)

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
        item = tags.li()
        anchor = item.add(tags.a(node.text))
        anchor["href"] = node.get_url()
        anchor["title"] = node.title
        anchor["class"] = node.aclass
        return item

    # all the below is from `Flask-Bootstrap.nav.BootstrapRenderer`
    # cannot be installed at the same time as `Bootstrap-Flask`
    # in order to avoid to many changes between migration, hard code
    # this instead of importing

    def visit_Subgroup(self, node: Subgroup) -> html_tag:
        """Render a subgroup.

        :return: An ``html_tag`` instance for rendering a subgroup.
        """
        li = tags.li()
        if not self._in_dropdown:
            li["class"] = "dropdown"
            a = li.add(tags.a(node.title, href="#", _class="dropdown-toggle"))
            a["data-toggle"] = "dropdown"
            a["role"] = "button"
            a["aria-haspopup"] = "true"
            a["aria-expanded"] = "false"
            a.add(tags.span(_class="caret"))

            ul = li.add(tags.ul(_class="dropdown-menu"))

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
        item = tags.li()
        item.add(tags.a(node.text, href=node.get_url(), title=node.text))
        if node.active:
            item["class"] = "active"

        return item
