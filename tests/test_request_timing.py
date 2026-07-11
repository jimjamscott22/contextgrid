"""Tests for request-duration logging middleware."""
from typing import List
import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.middleware import RequestTimingMiddleware


def _make_app(slow_ms: int = 200) -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestTimingMiddleware, slow_ms=slow_ms)

    @app.get("/api/fast")
    async def fast():
        return {"ok": True}

    @app.get("/api/slow")
    async def slow():
        import time
        time.sleep(0.05)
        return {"ok": True}

    return app


def test_logs_duration_for_successful_request(caplog):
    app = _make_app()
    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="api.timing"):
        response = client.get("/api/fast")
    assert response.status_code == 200
    matching: List[str] = [
        r.getMessage() for r in caplog.records if r.name == "api.timing"
    ]
    assert matching, "expected a timing log record"
    msg = matching[-1]
    assert "GET" in msg
    assert "/api/fast" in msg
    assert "200" in msg
    assert "ms" in msg


def test_warns_when_request_exceeds_threshold(caplog):
    app = _make_app(slow_ms=10)
    client = TestClient(app)
    with caplog.at_level(logging.WARNING, logger="api.timing"):
        response = client.get("/api/slow")
    assert response.status_code == 200
    warnings: List[str] = [
        r.getMessage()
        for r in caplog.records
        if r.name == "api.timing" and r.levelno >= logging.WARNING
    ]
    assert warnings, "expected a slow-request warning"
    assert "/api/slow" in warnings[-1]
