"""
app.utils.search
================
"""
from __future__ import annotations

import typing as t

from flask import current_app


def add_to_index(index: str, model) -> None:
    """Add searchable strings to search index.

    :param index: Index identifier.
    :param model: Database model to index strings for.
    """
    if current_app.elasticsearch is not None:  # type: ignore
        payload = {}
        for field in model.__searchable__:
            payload[field] = getattr(model, field)
        current_app.elasticsearch.index(  # type: ignore
            index=index, id=model.id, body=payload
        )


def remove_from_index(index: str, model) -> None:
    """Remove searchable strings from search index.

    :param index: Index identifier.
    :param model: Database model to remove strings for.
    """
    if current_app.elasticsearch is not None:  # type: ignore
        current_app.elasticsearch.delete(  # type: ignore
            index=index, id=model.id
        )


def query_index(
    index: str, expression: str, page: int, per_page: int
) -> t.Tuple[t.List[int], int]:
    """Query searchable strings in search index.

    :param index: Index identifier.
    :param expression: Search expression.
    :param page: Page number.
    :param per_page: Queries per page.
    :return: Tuple containing list of hit ids and search total value.
    """
    if current_app.elasticsearch is None:  # type: ignore
        return [], 0
    search = current_app.elasticsearch.search(  # type: ignore
        index=index,
        body={
            "query": {"multi_match": {"query": expression, "fields": ["*"]}},
            "from": (page - 1) * per_page,
            "size": per_page,
        },
    )
    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]
    return ids, search["hits"]["total"]["value"]
