"""Direct-mode list_projects SQL: tag+search must qualify project columns."""

from contextlib import contextmanager
from typing import Any, List, Optional

from src.db import MySQLBackend


class _FakeCursor:
    def __init__(self) -> None:
        self.query = ""
        self.params: Optional[List[Any]] = None

    def execute(self, query: str, params: Optional[List[Any]] = None) -> None:
        self.query = query
        self.params = params

    def fetchall(self) -> List[Any]:
        return []


def _backend_with_captured_cursor(monkeypatch):
    cursor = _FakeCursor()
    backend = MySQLBackend("localhost", 3306, "user", "pass", "contextgrid")

    @contextmanager
    def fake_cursor():
        yield cursor

    monkeypatch.setattr(backend, "_get_cursor", fake_cursor)
    return backend, cursor


def test_tag_and_search_qualifies_project_name_and_description(monkeypatch) -> None:
    backend, cursor = _backend_with_captured_cursor(monkeypatch)

    backend.list_projects(tag="python", search="grid")

    assert "p.name LIKE" in cursor.query
    assert "p.description" in cursor.query
    assert "AND (name LIKE" not in cursor.query
    assert "IFNULL(description," not in cursor.query


def test_search_without_tag_still_uses_projects_alias(monkeypatch) -> None:
    backend, cursor = _backend_with_captured_cursor(monkeypatch)

    backend.list_projects(search="grid")

    assert "FROM projects p" in cursor.query or "FROM projects p " in cursor.query
    assert "p.name LIKE" in cursor.query


def test_sort_columns_are_resolved_from_allowlist(monkeypatch) -> None:
    backend, cursor = _backend_with_captured_cursor(monkeypatch)

    backend.list_projects(sort_by="name", sort_order="asc")

    assert cursor.query.endswith(" ORDER BY p.name ASC, p.created_at DESC")


def test_created_at_sort_skips_secondary_tiebreak(monkeypatch) -> None:
    backend, cursor = _backend_with_captured_cursor(monkeypatch)

    backend.list_projects(sort_by="created_at", sort_order="asc")

    assert cursor.query.endswith(" ORDER BY p.created_at ASC")


def test_last_worked_at_keeps_nulls_first_case(monkeypatch) -> None:
    backend, cursor = _backend_with_captured_cursor(monkeypatch)

    backend.list_projects(sort_by="last_worked_at", sort_order="asc")

    assert (
        " ORDER BY CASE WHEN p.last_worked_at IS NULL THEN 0 ELSE 1 END ASC,"
        " p.last_worked_at ASC, p.created_at DESC"
    ) in cursor.query


def test_hostile_sort_inputs_fall_back_to_defaults(monkeypatch) -> None:
    backend, cursor = _backend_with_captured_cursor(monkeypatch)

    backend.list_projects(
        tag="python",
        sort_by="name; DROP TABLE projects",
        sort_order="ASC; DROP TABLE projects",
    )

    assert "DROP" not in cursor.query
    assert cursor.query.endswith(
        " ORDER BY CASE WHEN p.last_worked_at IS NULL THEN 0 ELSE 1 END DESC,"
        " p.last_worked_at DESC, p.created_at DESC"
    )
