"""
app.user
========

Functionality for user's of the app.
"""

from app.extensions import login_manager
from app.models import User, Usernames, db


def create_user(
    username: str, email: str, password: str, **kwargs: object
) -> User:
    """Instantiate a new user, add user to the database, and return.

    :param username: New user's username.
    :param email: New user's email address.
    :param password: New user's password.
    :param kwargs: Non-mandatory keyword arguments to pas to model.
    :return: New ``User`` object.
    """
    # noinspection PyArgumentList
    user = User(username=username, email=email, **kwargs)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    user = User.resolve_all_names(username=username)
    # noinspection PyArgumentList
    usernames = Usernames(username=user.username, user_id=user.id)
    db.session.add(usernames)
    db.session.commit()
    return user


@login_manager.user_loader
def user_login(id: int) -> User:
    """Wrap the user object.

    :param id: User id to get.
    :return: Returned user object.
    """
    return User.query.get(id)
