"""Gate tests for slowapi rate limiting on /api/v1/analyze."""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def fresh_client():
    """TestClient with a clean rate-limit storage before each test."""
    from services.api.store import store
    store._reports.clear()
    from services.api.main import app, limiter
    # Reset slowapi memory storage so tests start from zero
    try:
        limiter._limiter.storage.reset()
    except AttributeError:
        pass
    return TestClient(app)


def test_rate_limit_header_present(fresh_client):
    """Successful requests include X-RateLimit-Limit header (headers_enabled=True)."""
    resp = fresh_client.post("/api/v1/analyze", json={"riot_id": "Player#NA1"})
    assert resp.status_code == 200
    # slowapi injects rate limit headers when headers_enabled=True (case-insensitive check)
    header_names_lower = {h.lower() for h in resp.headers.keys()}
    assert "x-ratelimit-limit" in header_names_lower


def test_rate_limit_blocks_on_11th_request(fresh_client):
    """10 requests succeed; the 11th returns HTTP 429."""
    for i in range(10):
        resp = fresh_client.post("/api/v1/analyze", json={"riot_id": f"Player{i}#NA1"})
        assert resp.status_code == 200, f"Request {i+1} should return 200, got {resp.status_code}"

    resp = fresh_client.post("/api/v1/analyze", json={"riot_id": "Player10#NA1"})
    assert resp.status_code == 429


def test_rate_limit_429_body_is_json(fresh_client):
    """429 response body is valid JSON (not an HTML error page)."""
    for i in range(10):
        fresh_client.post("/api/v1/analyze", json={"riot_id": f"P{i}#NA1"})

    resp = fresh_client.post("/api/v1/analyze", json={"riot_id": "P10#NA1"})
    assert resp.status_code == 429
    assert resp.json()  # must be valid JSON
