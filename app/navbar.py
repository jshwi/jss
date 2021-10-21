"""
app.navbar
==========
"""
from dominate import tags
from flask import Flask, current_app
from flask_login import current_user
from flask_nav import register_renderer
from flask_nav.elements import Subgroup, View

from .extensions import nav
from .renderers import (
    BadgedView,
    ListGroup,
    Navbar,
    NavbarRenderer,
    RawUrl,
    Toggler,
)

# apply dark-mode from darkreader: https://darkreader.org/
# toggle CSS rules in templates/base.html
# ``onchange`` executes javascript function defined in static/js/main.js
# stylesheet attribute ``disabled`` is set to ``"disabled"`` by default
# when toggling dark-mode on, ``toggle_darkreader()`` will set the
# attribute to ``undefined`` and save the state with the javascript
# method ``localStorage.setItem`` to be retrieved on page refresh etc
# with ``localStorage.getItem``
TOGGLE_DARK_MODE = Toggler(
    "toggle-darkreader",
    id="toggle-darkreader",
    type="checkbox",
    data_toggle="toggle",
    data_onstyle="outline-dark",
    data_offstyle="outline-light",
    data_style="border",
    data_on="<i class='bi bi-sun'></i>",
    data_off="<i class='bi-moon'></i>",
    onchange="toggle_darkreader()",
)


def _construct_messages_view() -> BadgedView:
    # new messages will only be relevant if there are new messages
    # count won't be displayed if it is 0
    new_messages = current_user.new_messages()

    # instantiate a badge class to be processed in the navbar
    # visitor class
    badge = tags.span(new_messages, id="message_count")

    return BadgedView("Messages", new_messages, badge, "views.messages")


def _construct_user_subgroup() -> Subgroup:
    # construct a ``NavigationItem`` for implementing a group of links
    # in user specifically for a logged in user
    subgroup = ListGroup(current_user.username)

    # anything declared here will be in the navbar regardless of the
    # state of the current user i.e. admin is True or False.
    profile = View("Profile", "views.profile", username=current_user.username)
    logout = View("Logout", "auth.logout")

    # only available to admin user
    if current_user.admin:
        subgroup.items.append(RawUrl("Console", "/admin"))

    subgroup.items.extend([profile, logout])
    return subgroup


def top() -> Navbar:
    """Navbar positioned at the top of the page.

    Registered with the ``nav`` extension object in ``init_app`` to be
    processed as part of the navbar renderer.

    :return: Navbar object to register.
    """
    # construct the navbar
    brand = View(current_app.config["BRAND"], "index")
    navbar = Navbar(brand)

    # add the Home view to the navbar if configured to do so
    home = View("Home", "index")
    if current_app.config["NAVBAR_HOME"]:
        navbar.items.append(home)

    # anything declared here will be in the navbar regardless of the
    # state of the current user i.e. ``is_anonymous`` or
    # ``is_authenticated``
    navbar.header.append(TOGGLE_DARK_MODE)

    # the following will be rendered with the navbar if the user is
    # currently logged in
    if current_user.is_authenticated:
        messages = _construct_messages_view()
        create = View("New", "views.create")
        subgroup = _construct_user_subgroup()
        navbar.right_items.extend([messages, create, subgroup])
        return navbar

    # the following will be rendered with the navbar if the user is
    # not currently logged in
    register = View("Register", "auth.register")
    login = View("Login", "auth.login")
    navbar.right_items.extend([register, login])
    return navbar


def init_app(app: Flask) -> None:
    """Initialize navbar.

    :param app: Application factory object.
    """
    register_renderer(app, "navbar_renderer", NavbarRenderer)
    nav.register_element("top", top)
