"""
app.utils.register
==================

Contains registration utility class.
"""
from __future__ import annotations

import functools
import typing as t
from collections.abc import MutableMapping


class RegisterContext(MutableMapping):
    """Register context processor functions with instantiated object.

    Once instantiated all instances can be collected with the
    classmethod.

    Assigning a prefix will prevent the dictionary of combined key-value
    pairs from clashing with each other.

    :param prefix: Prefix collection keys.
    :param return_type: Instantiate a type with the return value of the
        registered function.
    """

    #: Index a collection of instantiations that contain the functions
    #: they have registered. Class instances contain attributes which
    #: make key-value pairs unique, and therefore if used correctly will
    #: not cause name collisions.
    _instances: t.List[RegisterContext] = []

    @classmethod
    def registered(cls) -> t.Dict[str, t.Callable[..., t.Any]]:
        """Get a dictionary of all registered items.

        :return: Dictionary of functions.
        """
        return dict(pair for d in cls._instances for pair in d.items())

    def __init__(
        self, prefix: t.Optional[str] = None, return_type: t.Type = str
    ) -> None:
        self._prefix = "" if prefix is None else f"{prefix}_"
        self._return_type = return_type
        self._dict: t.Dict[str, t.Callable[..., t.Any]] = {}
        self._instances.append(self)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._dict}>"

    def __len__(self) -> int:
        return self._dict.__len__()

    def __delitem__(self, key: t.Any) -> None:
        self._dict.__delitem__(key)

    def __setitem__(self, key: t.Any, value: t.Any) -> None:
        self._dict.__setitem__(key, value)

    def __getitem__(self, key: t.Any) -> t.Any:
        return self._dict.__getitem__(key)

    def __iter__(self) -> t.Iterator:
        return iter(self._dict)

    def register(self, func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
        """Register a function to be used in ``Jinja`` templates.

        :param func: Function to be callable from ``Jinja`` env.
        :return: Wrapped function
        """

        @functools.wraps(func)
        def _wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
            return self._return_type(func(*args, **kwargs))

        self[f"{self._prefix}{func.__name__}"] = _wrapper
        return _wrapper
