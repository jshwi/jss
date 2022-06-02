"""
app.utils.csp
=============
"""
import typing as t

CSPValType = t.Union[str, t.List[str]]
CSPType = t.MutableMapping[str, CSPValType]


class ContentSecurityPolicy(CSPType):
    """Object for setting default CSP and config override.

    :param default_csp: Default CSP, before implementing configurations.
    """

    def __init__(self, default_csp: t.Optional[CSPType] = None) -> None:
        self._dict: CSPType = default_csp or {}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._dict}>"

    def __len__(self) -> int:
        return self._dict.__len__()

    def __delitem__(self, key: str) -> None:
        self._dict.__delitem__(key)

    def __setitem__(self, key: str, value: CSPValType) -> None:
        self._dict.__setitem__(key, value)

    def __getitem__(self, key: str) -> CSPValType:
        return self._dict.__getitem__(key)

    def __iter__(self) -> t.Iterator[str]:
        return self._dict.__iter__()

    def _format_value(self, key, theirs) -> CSPValType:
        # start with a list, to combine "ours" and "theirs"
        value = []
        ours = self._dict.get(key)

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
            self._dict[key] = self._format_value(key, value)
