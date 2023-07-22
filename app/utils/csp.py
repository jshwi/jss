"""
app.utils.csp
=============
"""
from __future__ import annotations

import typing as t

CSPValType = t.Union[str, t.List[str]]
CSPType = t.Dict[str, CSPValType]


class ContentSecurityPolicy(CSPType):
    """Object for setting default CSP and config override.

    :param default_csp: Default CSP, before implementing configurations.
    """

    def __init__(self, default_csp: CSPType | None = None) -> None:
        super().__init__(default_csp or {})

    def _format_value(self, key: str, theirs: str | list[str]) -> CSPValType:
        # start with a list, to combine "ours" and "theirs"
        value = []
        ours = self.get(key)

        # loop through both to determine the types of each
        for item in theirs, ours:
            # if one of the items is a list concatenate it to the list
            # we are constructing
            if isinstance(item, list):
                value += item

            # if one of the items is a str append it to the list we are
            # constructing
            elif isinstance(item, str):
                value.append(item)

        # remove duplicates by converting the list to a set and then
        # back to a list again
        # for consistency and testing ensure the list is in
        # alphabetical / numerical order
        value = sorted(list(set(value)))

        # if there is only one item left after removing duplicates then
        # it can be the only item returned
        if len(value) == 1:
            return value[0]

        return value

    def update_policy(self, update: CSPType) -> None:
        """Combine a configured policy without overriding the existing.

        If the result is a single item, add a str.

        If the result is a list, remove duplicates and sort.

        If either is a str and the other is a list, add the str and the
        list contents to the new list.

        If both are str values add to the new list.

        :param update: A str or a list of str objects.
        """
        for key, value in update.items():
            self[key] = self._format_value(key, value)
