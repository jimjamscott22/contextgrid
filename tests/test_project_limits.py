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
    ) -> List[Dict[str, Any]]:
        captured["limit"] = limit
        return []

    monkeypatch.setattr(db, "list_projects", fake_list_projects)

    client = TestClient(app)
    response = client.get("/api/projects?include_archived=true&limit=500")

    assert response.status_code == 200
    assert captured["limit"] == 50
