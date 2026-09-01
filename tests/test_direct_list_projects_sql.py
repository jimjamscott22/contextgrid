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
