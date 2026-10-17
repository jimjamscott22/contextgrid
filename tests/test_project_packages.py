"""
Tests for project package manager and project package API endpoints.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from api import db
from api.server import app


def _sample_project(
    project_id: int = 1,
    name: str = "Demo",
    package_manager: Optional[str] = "uv",
) -> Dict[str, Any]:
    return {
        "id": project_id,
        "name": name,
        "description": None,
        "status": "active",
        "project_type": "web-app",
        "primary_language": "Python",
        "stack": "FastAPI + React",
        "repo_url": None,
        "local_path": None,
        "scope_size": "medium",
        "learning_goal": None,
        "progress": 50,
        "folder_structure": None,
        "folder_structure_img_url": None,
        "package_manager": package_manager,
        "created_at": "2026-01-01T00:00:00",
        "last_worked_at": None,
        "is_archived": 0,
        "open_task_count": 0,
    }


def _sample_package(
    pkg_id: int = 10,
    project_id: int = 1,
    name: str = "fastapi",
    version: Optional[str] = ">=0.115.0",
    package_type: str = "prod",
    description: Optional[str] = "REST API framework",
) -> Dict[str, Any]:
    return {
        "id": pkg_id,
        "project_id": project_id,
        "name": name,
        "version": version,
        "package_type": package_type,
        "description": description,
        "created_at": "2026-01-01T00:00:00",
    }


def test_create_project_persists_package_manager(monkeypatch) -> None:
    """POST /api/projects forwards package_manager to db.create_project."""
    captured: Dict[str, Any] = {}

    def fake_create_project(**kwargs: Any) -> int:
        captured.update(kwargs)
        return 1

    monkeypatch.setattr(db, "create_project", fake_create_project)
    monkeypatch.setattr(
        db,
        "get_project",
        lambda pid: _sample_project(project_id=pid, package_manager=captured.get("package_manager")),
    )

    client = TestClient(app)
    res = client.post(
        "/api/projects",
        json={"name": "My App", "status": "active", "package_manager": "pnpm"},
    )

    assert res.status_code == 201
    assert captured["package_manager"] == "pnpm"
    assert res.json()["package_manager"] == "pnpm"


def test_update_project_updates_package_manager(monkeypatch) -> None:
    """PUT /api/projects/{id} updates package_manager."""
    captured: Dict[str, Any] = {}

    monkeypatch.setattr(
        db,
        "get_project",
        lambda pid: _sample_project(
            project_id=pid,
            package_manager=captured.get("package_manager", "npm"),
        ),
    )

    def fake_update_project(project_id: int, **kwargs: Any) -> bool:
        captured.update(kwargs)
        return True

    monkeypatch.setattr(db, "update_project", fake_update_project)

    client = TestClient(app)
    res = client.put("/api/projects/1", json={"package_manager": "cargo"})

    assert res.status_code == 200
    assert captured["package_manager"] == "cargo"
    assert res.json()["package_manager"] == "cargo"


def test_update_project_clears_package_manager_when_null_or_empty(monkeypatch) -> None:
    """PUT /api/projects/{id} clears package_manager when sent as null or empty."""
    state: Dict[str, Any] = {"package_manager": "uv"}
    captured_calls: List[Dict[str, Any]] = []

    monkeypatch.setattr(
        db,
        "get_project",
        lambda pid: _sample_project(
            project_id=pid,
            package_manager=state["package_manager"],
        ),
    )

    def fake_update_project(project_id: int, **kwargs: Any) -> bool:
        captured_calls.append(dict(kwargs))
        state.update(kwargs)
        return True

    monkeypatch.setattr(db, "update_project", fake_update_project)

    client = TestClient(app)

    res_null = client.put(
        "/api/projects/1",
        json={"name": "Demo", "status": "active", "package_manager": None},
    )
    assert res_null.status_code == 200
    assert "package_manager" in captured_calls[-1]
    assert captured_calls[-1]["package_manager"] is None
    assert res_null.json()["package_manager"] is None

    state["package_manager"] = "pnpm"
    res_blank = client.put("/api/projects/1", json={"package_manager": "   "})
    assert res_blank.status_code == 200
    assert "package_manager" in captured_calls[-1]
    assert captured_calls[-1]["package_manager"] is None
    assert res_blank.json()["package_manager"] is None


def test_list_project_packages(monkeypatch) -> None:
    """GET /api/projects/{id}/packages returns all packages for the project."""
    monkeypatch.setattr(db, "get_project", lambda pid: _sample_project(project_id=pid))
    monkeypatch.setattr(
        db,
        "list_project_packages",
        lambda pid: [
            _sample_package(pkg_id=1, project_id=pid, name="fastapi", package_type="prod"),
            _sample_package(pkg_id=2, project_id=pid, name="pytest", package_type="dev"),
        ],
    )

    client = TestClient(app)
    res = client.get("/api/projects/1/packages")

    assert res.status_code == 200
    payload = res.json()
    assert payload["total"] == 2
    assert [p["name"] for p in payload["packages"]] == ["fastapi", "pytest"]


def test_list_project_packages_404_when_project_missing(monkeypatch) -> None:
    """GET /api/projects/{id}/packages returns 404 for unknown project."""
    monkeypatch.setattr(db, "get_project", lambda _pid: None)

    client = TestClient(app)
    res = client.get("/api/projects/999/packages")

    assert res.status_code == 404


def test_create_project_package(monkeypatch) -> None:
    """POST /api/projects/{id}/packages creates and returns a package."""
    captured: Dict[str, Any] = {}

    monkeypatch.setattr(db, "get_project", lambda pid: _sample_project(project_id=pid))

    def fake_create_package(**kwargs: Any) -> int:
        captured.update(kwargs)
        return 42

    monkeypatch.setattr(db, "create_package", fake_create_package)
    monkeypatch.setattr(
        db,
        "get_package",
        lambda pkg_id: _sample_package(
            pkg_id=pkg_id,
            project_id=captured["project_id"],
            name=captured["name"],
            version=captured["version"],
            package_type=captured["package_type"],
            description=captured["description"],
        ),
    )

    client = TestClient(app)
    res = client.post(
        "/api/projects/1/packages",
        json={
            "name": "  @tanstack/react-query  ",
            "version": " ^5.62.0 ",
            "package_type": "prod",
            "description": " Async state management ",
        },
    )

    assert res.status_code == 201
    data = res.json()
    assert data["id"] == 42
    assert data["name"] == "@tanstack/react-query"
    assert data["version"] == "^5.62.0"
    assert data["package_type"] == "prod"
    assert data["description"] == "Async state management"


def test_update_project_package(monkeypatch) -> None:
    """PUT /api/packages/{id} updates package fields."""
    captured: Dict[str, Any] = {}

    monkeypatch.setattr(
        db,
        "get_package",
        lambda pkg_id: _sample_package(
            pkg_id=pkg_id,
            name=captured.get("name", "fastapi"),
            version=captured.get("version", ">=0.115.0"),
            package_type=captured.get("package_type", "prod"),
            description=captured.get("description", "REST API framework"),
        ),
    )

    def fake_update_package(package_id: int, **kwargs: Any) -> bool:
        captured.update(kwargs)
        return True

    monkeypatch.setattr(db, "update_package", fake_update_package)

    client = TestClient(app)
    res = client.put(
        "/api/packages/10",
        json={"version": ">=0.116.0", "package_type": "dev", "description": "Updated"},
    )

    assert res.status_code == 200
    data = res.json()
    assert data["version"] == ">=0.116.0"
    assert data["package_type"] == "dev"
    assert data["description"] == "Updated"


def test_delete_project_package(monkeypatch) -> None:
    """DELETE /api/packages/{id} deletes the package or returns 404."""
    monkeypatch.setattr(db, "delete_package", lambda pkg_id: pkg_id == 10)

    client = TestClient(app)
    ok_res = client.delete("/api/packages/10")
    assert ok_res.status_code == 200

    missing_res = client.delete("/api/packages/999")
    assert missing_res.status_code == 404


def test_create_project_package_rejects_whitespace_only_name(monkeypatch) -> None:
    """POST /api/projects/{id}/packages rejects names that are empty after trimming."""
    monkeypatch.setattr(db, "get_project", lambda pid: _sample_project(project_id=pid))
    called = False

    def fake_create_package(**kwargs: Any) -> int:
        nonlocal called
        called = True
        return 1

    monkeypatch.setattr(db, "create_package", fake_create_package)

    client = TestClient(app)
    res = client.post(
        "/api/projects/1/packages",
        json={"name": "   \t  ", "version": "1.0.0", "package_type": "prod"},
    )

    assert res.status_code == 422
    assert not called


def test_update_project_package_rejects_whitespace_only_name(monkeypatch) -> None:
    """PUT /api/packages/{id} rejects names that are empty after trimming."""
    monkeypatch.setattr(db, "get_package", lambda pkg_id: _sample_package(pkg_id=pkg_id))
    called = False

    def fake_update_package(package_id: int, **kwargs: Any) -> bool:
        nonlocal called
        called = True
        return True

    monkeypatch.setattr(db, "update_package", fake_update_package)

    client = TestClient(app)
    res = client.put("/api/packages/10", json={"name": "   "})

    assert res.status_code == 422
    assert not called
