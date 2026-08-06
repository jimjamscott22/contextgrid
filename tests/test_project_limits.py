"""
Tests for project list request limits.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from api import db
from api.server import app


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
    ) -> List[Dict[str, Any]]:
        captured["limit"] = limit
        captured["include_archived"] = include_archived
        return []

    monkeypatch.setattr(db, "list_projects", fake_list_projects)

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
    ) -> List[Dict[str, Any]]:
        captured["include_archived"] = include_archived
        return []

    monkeypatch.setattr(db, "list_projects", fake_list_projects)

    client = TestClient(app)

    # Default should be False
    res1 = client.get("/api/projects")
    assert res1.status_code == 200
    assert captured["include_archived"] is False

    # Setting to true should pass True
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
    ) -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "name": "Demo",
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
        ]

    monkeypatch.setattr(db, "list_projects", fake_list_projects)

    client = TestClient(app)
    response = client.get("/api/projects")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["projects"][0]["open_task_count"] == 3
