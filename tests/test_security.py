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
