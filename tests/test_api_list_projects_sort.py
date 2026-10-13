"""API-layer list_projects ORDER BY: sort inputs resolve via a fixed allowlist."""

from contextlib import contextmanager
from typing import Any, List, Optional

import pytest

from api import db


class _FakeCursor:
    def __init__(self) -> None:
        self.query = ""
        self.params: Optional[List[Any]] = None

    def execute(self, query: str, params: Optional[List[Any]] = None) -> None:
        self.query = query
        self.params = params

    def fetchall(self) -> List[Any]:
        return []


def _run(monkeypatch, **kwargs: Any) -> str:
    cursor = _FakeCursor()

    @contextmanager
    def fake_cursor():
        yield cursor

    monkeypatch.setattr(db, "get_db_cursor", fake_cursor)
    db.list_projects(**kwargs)
    return cursor.query


@pytest.mark.parametrize(
    "sort_by,order,expected",
    [
        ("name", "asc", " ORDER BY p.name ASC, p.created_at DESC"),
        ("status", "DESC", " ORDER BY p.status DESC, p.created_at DESC"),
        ("created_at", "asc", " ORDER BY p.created_at ASC"),
    ],
)
def test_sort_columns_are_resolved_from_allowlist(
    monkeypatch, sort_by: str, order: str, expected: str
) -> None:
    query = _run(monkeypatch, sort_by=sort_by, sort_order=order)

    assert query.endswith(expected)


def test_last_worked_at_keeps_nulls_first_case(monkeypatch) -> None:
    query = _run(monkeypatch, sort_by="last_worked_at", sort_order="asc")

    assert (
        " ORDER BY CASE WHEN p.last_worked_at IS NULL THEN 0 ELSE 1 END ASC,"
        " p.last_worked_at ASC, p.created_at DESC"
    ) in query


@pytest.mark.parametrize(
    "sort_by,order,expected",
    [
        (
            "name; DROP TABLE projects",
            "asc",
            " ORDER BY CASE WHEN p.last_worked_at IS NULL THEN 0 ELSE 1 END ASC,"
            " p.last_worked_at ASC, p.created_at DESC",
        ),
        ("name", "ASC; DROP TABLE projects", " ORDER BY p.name DESC, p.created_at DESC"),
        (
            "",
            "",
            " ORDER BY CASE WHEN p.last_worked_at IS NULL THEN 0 ELSE 1 END DESC,"
            " p.last_worked_at DESC, p.created_at DESC",
        ),
    ],
)
def test_unknown_sort_inputs_fall_back_to_defaults(
    monkeypatch, sort_by: str, order: str, expected: str
) -> None:
    query = _run(monkeypatch, sort_by=sort_by, sort_order=order)

    assert "DROP" not in query
    assert query.endswith(expected)
