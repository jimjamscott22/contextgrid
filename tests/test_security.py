# tests/test_security.py


# ── CORS ──────────────────────────────────────────────────────────────────

def test_cors_disallowed_origin_not_echoed(api_client):
    resp = api_client.options(
        "/api/health",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.headers.get("access-control-allow-origin") != "http://evil.example.com"


def test_cors_allowed_origin_echoed(api_client):
    resp = api_client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_credentials_not_sent(api_client):
    resp = api_client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    # allow_credentials=False means this header must not say "true"
    assert resp.headers.get("access-control-allow-credentials") != "true"


import io
from unittest.mock import patch, AsyncMock


# ── SVG rejection ─────────────────────────────────────────────────────────

def test_svg_rejected_by_extension(api_client):
    resp = api_client.post(
        "/api/projects/1/screenshots",
        files={"file": ("diagram.svg", b"<svg/>", "image/png")},
    )
    assert resp.status_code == 400


def test_svg_rejected_by_content_type(api_client):
    resp = api_client.post(
        "/api/projects/1/screenshots",
        files={"file": ("diagram.svg", b"<svg/>", "image/svg+xml")},
    )
    assert resp.status_code == 400


# ── Upload size cap ───────────────────────────────────────────────────────

def test_upload_over_cap_returns_413(api_client, tmp_path):
    from api.config import config as api_config

    large = b"x" * (10 * 1024 * 1024 + 1)  # 10 MB + 1 byte
    with patch.object(api_config, "UPLOADS_DIR", tmp_path / "uploads"):
        resp = api_client.post(
            "/api/projects/1/screenshots",
            files={"file": ("shot.png", large, "image/png")},
        )
    assert resp.status_code == 413


def test_upload_at_cap_succeeds(api_client, tmp_path):
    from api.config import config as api_config

    at_cap = b"x" * (10 * 1024 * 1024)  # exactly 10 MB
    with patch.object(api_config, "UPLOADS_DIR", tmp_path / "uploads"):
        resp = api_client.post(
            "/api/projects/1/screenshots",
            files={"file": ("shot.png", at_cap, "image/png")},
        )
    assert resp.status_code == 200


def test_upload_over_cap_leaves_no_partial_file(api_client, tmp_path):
    from api.config import config as api_config

    upload_dir = tmp_path / "uploads"
    large = b"x" * (10 * 1024 * 1024 + 1)
    with patch.object(api_config, "UPLOADS_DIR", upload_dir):
        api_client.post(
            "/api/projects/1/screenshots",
            files={"file": ("shot.png", large, "image/png")},
        )
    # No partial file should exist
    project_dir = upload_dir / "1"
    png_files = list(project_dir.glob("*.png")) if project_dir.exists() else []
    assert png_files == []


# ── README size cap ───────────────────────────────────────────────────────

def test_readme_over_cap_returns_413(api_client):
    big_content = "x" * (1024 * 1024 + 1)  # 1 MB + 1 byte
    with (
        patch(
            "api.server._fetch_github_readme",
            new_callable=AsyncMock,
            return_value=(big_content, "main"),
        ),
        patch(
            "api.db.get_project",
            return_value={"id": 1, "repo_url": "https://github.com/test/repo"},
        ),
    ):
        resp = api_client.post("/api/projects/1/readme/attach")
    assert resp.status_code == 413


def test_readme_under_cap_stores_snapshot(api_client):
    content = "# Test README"
    with (
        patch(
            "api.server._fetch_github_readme",
            new_callable=AsyncMock,
            return_value=(content, "main"),
        ),
        patch(
            "api.db.get_project",
            return_value={"id": 1, "repo_url": "https://github.com/test/repo"},
        ),
        patch("api.db.upsert_readme_snapshot", return_value=None),
        patch(
            "api.db.get_readme_snapshot",
            return_value={
                "project_id": 1,
                "content": content,
                "source_ref": "main",
                "fetched_at": "2026-01-01T00:00:00",
            },
        ),
    ):
        resp = api_client.post("/api/projects/1/readme/attach")
    assert resp.status_code == 200
