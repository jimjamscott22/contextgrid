"""Tests for optional API bearer-token authentication."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def auth_api_client():
    """Test client with auth enabled via a fixed API_TOKEN."""
    with (
        patch("api.db.test_connection", return_value=(True, None)),
        patch("api.db.initialize_database", return_value=None),
        patch("api.config.Config.validate", return_value=(True, None)),
        patch("api.config.config.API_TOKEN", "test-secret-token"),
    ):
        from api.server import app

        with TestClient(app) as client:
            yield client


def test_api_requires_bearer_when_token_configured(auth_api_client):
    resp = auth_api_client.get("/api/health")
    assert resp.status_code == 401

    resp = auth_api_client.get(
        "/api/health",
        headers={"Authorization": "Bearer test-secret-token"},
    )
    assert resp.status_code == 200


def test_uploads_require_bearer_or_query_token(auth_api_client):
    resp = auth_api_client.get("/uploads/1/example.png")
    assert resp.status_code == 401

    resp = auth_api_client.get(
        "/uploads/1/example.png",
        headers={"Authorization": "Bearer test-secret-token"},
    )
    # File may not exist; auth should pass before static handler returns 404.
    assert resp.status_code == 404

    resp = auth_api_client.get("/uploads/1/example.png?token=test-secret-token")
    assert resp.status_code == 404


def test_non_loopback_bind_requires_api_token():
    from api.config import Config

    with (
        patch.object(Config, "DB_PASSWORD", "secret"),
        patch.object(Config, "DB_USER", "user"),
        patch.object(Config, "API_HOST", "0.0.0.0"),
        patch.object(Config, "API_TOKEN", None),
    ):
        valid, error = Config.validate()
        assert not valid
        assert "API_TOKEN" in (error or "")


def test_loopback_bind_allows_missing_api_token():
    from api.config import Config

    with (
        patch.object(Config, "DB_PASSWORD", "secret"),
        patch.object(Config, "DB_USER", "user"),
        patch.object(Config, "API_HOST", "127.0.0.1"),
        patch.object(Config, "API_TOKEN", None),
    ):
        valid, error = Config.validate()
        assert valid
        assert error is None
