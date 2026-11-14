"""Saved project group validation, API forwarding, and SQL persistence."""

from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api import db
from api.models import ProjectCreate, ProjectUpdate
from api.server import app
from src.db import MySQLBackend


def test_group_normalization_and_length() -> None:
    """Group names are bounded and whitespace-only values clear assignments."""
    assert ProjectCreate(name="Demo", project_group=" Work ").project_group == "Work"
    assert ProjectUpdate(project_group="  ").project_group is None
    assert "project_group" not in ProjectUpdate(name="Demo").model_dump(exclude_unset=True)
    with pytest.raises(ValidationError):
        ProjectCreate(name="Demo", project_group="x" * 101)


def test_group_api_create_update_and_clear(monkeypatch) -> None:
    """The API preserves an omitted group and saves explicit changes and clears."""
    state = {"id": 1, "name": "Demo", "created_at": "2026-01-01", "project_group": None}

    def create(**kwargs):
        state.update(kwargs)
        return 1

    def update(project_id, **kwargs):
        state.update(kwargs)
        return True

    monkeypatch.setattr(db, "create_project", create)
    monkeypatch.setattr(db, "update_project", update)
    monkeypatch.setattr(db, "get_project", lambda project_id: dict(state))
    client = TestClient(app)
    response = client.post("/api/projects", json={"name": "Demo", "project_group": " Work "})
    assert response.status_code == 201
    assert response.json()["project_group"] == "Work"
    assert client.put("/api/projects/1", json={"name": "Renamed"}).json()["project_group"] == "Work"
    assert client.put("/api/projects/1", json={"project_group": "Learning"}).json()["project_group"] == "Learning"
    for value in [None, "", "  "]:
        state["project_group"] = "Work"
        response = client.put("/api/projects/1", json={"project_group": value})
        assert response.status_code == 200
        assert response.json()["project_group"] is None


@pytest.mark.parametrize("mode", ["api", "direct"])
def test_group_sql_is_parameterized(monkeypatch, mode: str) -> None:
    """Both database entry points persist group names through query parameters."""
    cursor = MagicMock(lastrowid=1, rowcount=1)

    @contextmanager
    def get_cursor():
        yield cursor

    if mode == "api":
        monkeypatch.setattr(db, "get_db_cursor", get_cursor)
        backend = db
    else:
        backend = MySQLBackend.__new__(MySQLBackend)
        monkeypatch.setattr(backend, "_get_cursor", get_cursor)
    group = "Work's projects"
    assert backend.create_project(name="Demo", project_group=group) == 1
    sql, params = cursor.execute.call_args.args
    assert "project_group" in sql
    assert group not in sql
    assert group in params
    assert sql.count("%s") == len(params)
    assert backend.update_project(1, project_group=None)
    sql, params = cursor.execute.call_args.args
    assert "project_group = %s" in sql
    assert list(params) == [None, 1]
