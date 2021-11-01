"""
app.utils.register
==================

Contains registration utility class.
"""
from __future__ import annotations

import functools
from collections.abc import MutableMapping
from typing import Any, Callable, Dict, Iterator, List, Optional, Type


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
    _instances: List[RegisterContext] = []

    @classmethod
    def registered(cls) -> Dict[str, Callable[..., Any]]:
        """Get a dictionary of all registered items.

        :return: Dictionary of functions.
        """
        return dict(pair for d in cls._instances for pair in d.items())

    def __init__(
        self, prefix: Optional[str] = None, return_type: Type = str
    ) -> None:
        self._prefix = "" if prefix is None else f"{prefix}_"
        self._return_type = return_type
        self._dict: Dict[str, Callable[..., Any]] = {}
        self._instances.append(self)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._dict}>"

    def __len__(self) -> int:
        return self._dict.__len__()

    def __delitem__(self, key: Any) -> None:
        self._dict.__delitem__(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        self._dict.__setitem__(key, value)

    def __getitem__(self, key: Any) -> Any:
        return self._dict.__getitem__(key)

    def __iter__(self) -> Iterator:
        return iter(self._dict)

    def register(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Register a function to be used in ``Jinja`` templates.

        :param func: Function to be callable from ``Jinja`` env.
        :return: Wrapped function
        """

        @functools.wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return self._return_type(func(*args, **kwargs))

        self[f"{self._prefix}{func.__name__}"] = _wrapper
        return _wrapper
