"""
Tests for project list request limits, totals, and search.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from api import db
from api.server import app


def _sample_project(project_id: int = 1, name: str = "Demo") -> Dict[str, Any]:
    return {
        "id": project_id,
        "name": name,
        "description": None,
        "status": "active",
        "project_type": None,
        "primary_language": None,
        "stack": None,
        "repo_url": None,
        "local_path": None,
        "scope_size": None,
        "learning_goal": None,
        "progress": 0,
        "folder_structure": None,
        "folder_structure_img_url": None,
        "created_at": "2026-01-01T00:00:00",
        "last_worked_at": None,
        "is_archived": 0,
        "open_task_count": 3,
    }


def _patch_list_and_count(monkeypatch, fake_list, count_value=0):
    monkeypatch.setattr(db, "list_projects", fake_list)
    monkeypatch.setattr(db, "count_projects", lambda **_kwargs: count_value)


def test_project_list_caps_oversized_limit(monkeypatch) -> None:
    """Oversized project list requests should be accepted and capped."""
    captured: Dict[str, Any] = {}

    def fake_list_projects(
        status: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: str = "last_worked_at",
        sort_order: str = "desc",
        include_archived: bool = False,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        captured["limit"] = limit
        captured["include_archived"] = include_archived
        return []

    _patch_list_and_count(monkeypatch, fake_list_projects, 0)

    client = TestClient(app)
    response = client.get("/api/projects?include_archived=true&limit=500")

    assert response.status_code == 200
    assert captured["limit"] == 50
    assert captured["include_archived"] is True


def test_project_list_passes_include_archived(monkeypatch) -> None:
    """include_archived query param should be passed down to db.list_projects."""
    captured: Dict[str, Any] = {}

    def fake_list_projects(
        status: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: str = "last_worked_at",
        sort_order: str = "desc",
        include_archived: bool = False,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        captured["include_archived"] = include_archived
        return []

    _patch_list_and_count(monkeypatch, fake_list_projects, 0)

    client = TestClient(app)

    res1 = client.get("/api/projects")
    assert res1.status_code == 200
    assert captured["include_archived"] is False

    res2 = client.get("/api/projects?include_archived=true")
    assert res2.status_code == 200
    assert captured["include_archived"] is True


def test_project_list_includes_open_task_count(monkeypatch) -> None:
    """Project list responses should expose incomplete checklist task counts."""

    def fake_list_projects(
        status: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: str = "last_worked_at",
        sort_order: str = "desc",
        include_archived: bool = False,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return [_sample_project()]

    _patch_list_and_count(monkeypatch, fake_list_projects, 1)

    client = TestClient(app)
    response = client.get("/api/projects")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["projects"][0]["open_task_count"] == 3


def test_project_list_total_is_unpaginated_count(monkeypatch) -> None:
    """total must be the matching-row count, not the length of the current page."""

    def fake_list_projects(
        status: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: str = "last_worked_at",
        sort_order: str = "desc",
        include_archived: bool = False,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return [_sample_project()]

    _patch_list_and_count(monkeypatch, fake_list_projects, 3)

    client = TestClient(app)
    response = client.get("/api/projects?limit=1")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["projects"]) == 1
    assert payload["total"] == 3


def test_project_list_passes_search(monkeypatch) -> None:
    """search query param should be passed to list and count."""
    captured: Dict[str, Any] = {}

    def fake_list_projects(
        status: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: str = "last_worked_at",
        sort_order: str = "desc",
        include_archived: bool = False,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        captured["list_search"] = search
        return []

    def fake_count_projects(**kwargs: Any) -> int:
        captured["count_search"] = kwargs.get("search")
        return 0

    monkeypatch.setattr(db, "list_projects", fake_list_projects)
    monkeypatch.setattr(db, "count_projects", fake_count_projects)

    client = TestClient(app)
    response = client.get("/api/projects?search=contextgrid")

    assert response.status_code == 200
    assert captured["list_search"] == "contextgrid"
    assert captured["count_search"] == "contextgrid"
