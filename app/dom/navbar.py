"""
app.dom.navbar
==============
"""
from dominate import tags
from flask import current_app
from flask_login import current_user
from flask_nav.elements import Subgroup, View

from app.dom.renderers import BadgedView, IconView, ListGroup, Navbar, RawUrl


def _construct_messages_view() -> BadgedView:
    # new messages will only be relevant if there are new messages
    # count won't be displayed if it is 0
    new_messages = current_user.new_messages()

    # instantiate a badge class to be processed in the navbar
    # visitor class
    badge = tags.span(new_messages, id="message_count")

    return BadgedView("Messages", new_messages, badge, "user.messages")


def _construct_user_subgroup() -> Subgroup:
    # construct a ``NavigationItem`` for implementing a group of links
    # in user specifically for a logged-in user
    if current_app.config["NAVBAR_USER_DROPDOWN"]:

        subgroup = Subgroup(
            tags.img(src=current_user.avatar(18), cls="navbar-avatar")
        )
    else:
        subgroup = ListGroup(current_user.username)

    # anything declared here will be in the navbar regardless of the
    # state of the current user i.e. admin is True or False.
    profile = View("Profile", "public.profile", username=current_user.username)
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

    # the following will be rendered with the navbar if the user is
    # currently logged in
    if current_user.is_authenticated:
        messages = _construct_messages_view()
        create = IconView("New", "post.create")
        subgroup = _construct_user_subgroup()

        # replace regular text with icon attributes if configured to do
        # so
        if current_app.config["NAVBAR_ICONS"]:
            messages.set_icon("bi-bell")
            create.set_icon("bi-plus-lg")

        navbar.right_items.extend([messages, create, subgroup])
        return navbar

    # the following will be rendered with the navbar if the user is
    # not currently logged in
    register = View("Register", "auth.register")
    login = View("Login", "auth.login")
    navbar.right_items.extend([register, login])
    return navbar
