"""Legacy web UI: project redirects stay local; kanban errors don't leak details."""

from fastapi.testclient import TestClient

from web import app as web_app
from web.app import app as legacy_app


def _boom(*args, **kwargs):
    raise RuntimeError("secret db detail: host=10.0.0.5")


def test_redirect_helper_builds_local_project_path() -> None:
    response = web_app._redirect_to_project(42)

    assert response.status_code == 303
    assert response.headers["location"] == "/projects/42"


def test_readme_delete_redirects_to_project_detail(monkeypatch) -> None:
    async def ok(project_id: int) -> bool:
        return True

    monkeypatch.setattr(web_app.models, "delete_readme_snapshot", ok)

    with TestClient(legacy_app) as client:
        response = client.post("/projects/7/readme/delete", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/projects/7"


def test_non_integer_project_id_is_rejected_before_redirect() -> None:
    with TestClient(legacy_app) as client:
        response = client.post(
            "/projects/https:%2F%2Fevil.example/readme/delete", follow_redirects=False
        )

    assert response.status_code in (404, 422)
    assert "evil.example" not in response.headers.get("location", "")


def test_kanban_move_error_does_not_expose_exception_text(monkeypatch) -> None:
    monkeypatch.setattr(web_app.models, "update_project", _boom)

    with TestClient(legacy_app) as client:
        response = client.post(
            "/api/kanban/move", json={"project_id": 1, "status": "active"}
        )

    assert response.status_code == 500
    assert "secret db detail" not in response.text
    assert response.json() == {"error": "Failed to update project"}
