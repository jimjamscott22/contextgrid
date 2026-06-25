# tests/conftest.py
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def api_client():
    """FastAPI TestClient with DB mocked out — no real database required."""
    with (
        patch("api.db.test_connection", return_value=(True, None)),
        patch("api.db.initialize_database", return_value=None),
        patch("api.config.Config.validate", return_value=(True, None)),
    ):
        from api.server import app
        with TestClient(app) as client:
            yield client
