"""Gate tests for the FastAPI backend — mocked riot + llm, no external calls."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import asyncio
import dataclasses
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from contracts.schemas import RiotReport, CoachingReport, MatchStat


MOCK_RIOT_REPORT = RiotReport(
    puuid="mock-puuid",
    game_name="TestPlayer",
    tag_line="NA1",
    current_rank="Gold 2",
    rank_delta=15,
    matches=[MatchStat("m1","Jett","Vandal",18,12,3,25.0,160.0,True)],
    avg_headshot_pct=25.0,
    avg_adr=160.0,
    top_agent="Jett",
    top_weapon="Vandal",
    win_rate=0.6,
)

MOCK_COACHING = CoachingReport(
    summary="Good player, needs headshot improvement.",
    top_weakness="HS% of 25% below Gold average.",
    tips=["Keep crosshair at head height.", "Burst fire at range."],
    encouragement="Keep grinding.",
    raw_response="{}",
)


@pytest.fixture
def client():
    # Reset store between tests
    from services.api.store import store
    store._reports.clear()
    from services.api.main import app
    return TestClient(app)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_submit_analysis_returns_report_id(client):
    resp = client.post("/api/v1/analyze", json={"riot_id": "TestPlayer#NA1"})
    assert resp.status_code == 200
    data = resp.json()
    assert "report_id" in data
    assert data["status"] in ("queued", "processing", "done")


def test_submit_analysis_invalid_riot_id(client):
    resp = client.post("/api/v1/analyze", json={"riot_id": "NoHashHere"})
    assert resp.status_code == 422


def test_get_report_not_found(client):
    resp = client.get("/api/v1/report/nonexistent-id")
    assert resp.status_code == 404


def test_full_analysis_flow(client):
    """Submit → poll until done (with mocked services)."""
    # Patch at the source modules — they are imported inside _run_analysis() each call
    with (
        patch("services.riot.service.get_riot_report",   new=AsyncMock(return_value=MOCK_RIOT_REPORT)),
        patch("services.llm.coach.generate_coaching_report", new=AsyncMock(return_value=MOCK_COACHING)),
    ):
        # Submit
        resp = client.post("/api/v1/analyze", json={"riot_id": "TestPlayer#NA1"})
        assert resp.status_code == 200
        report_id = resp.json()["report_id"]

        # Background task runs synchronously in TestClient
        # Poll for result
        import time
        for _ in range(10):
            r = client.get(f"/api/v1/report/{report_id}")
            assert r.status_code == 200
            if r.json()["status"] == "done":
                break
            time.sleep(0.1)

        result = client.get(f"/api/v1/report/{report_id}").json()
        assert result["status"] == "done"
        assert result["riot_report"] is not None
        assert result["coaching"] is not None


def test_auth_endpoints_return_501(client):
    resp = client.post("/api/v1/auth/magic-link", json={"email": "test@example.com"})
    assert resp.status_code == 501

    resp = client.post("/api/v1/auth/riot-id", json={"riot_id": "Name#TAG"})
    assert resp.status_code == 501


# ------------------------------------------------------------------ #
# Dev bypass
# ------------------------------------------------------------------ #

def test_dev_create_account_returns_token(monkeypatch, client):
    import services.api.main as main_mod
    monkeypatch.setattr(main_mod, "DEV_MODE", True)
    resp = client.post("/api/v1/dev/create-account", json={"email": "dev@test.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["user"]["email"] == "dev@test.com"


def test_dev_create_account_disabled_returns_404(monkeypatch, client):
    import services.api.main as main_mod
    monkeypatch.setattr(main_mod, "DEV_MODE", False)
    resp = client.post("/api/v1/dev/create-account", json={"email": "x@x.com"})
    assert resp.status_code == 404


def test_dev_get_session_valid_token(monkeypatch, client):
    import services.api.main as main_mod
    monkeypatch.setattr(main_mod, "DEV_MODE", True)
    # Create account first
    create = client.post("/api/v1/dev/create-account", json={"email": "s@s.com"})
    token = create.json()["token"]
    # Look it up
    resp = client.get(f"/api/v1/dev/session?token={token}")
    assert resp.status_code == 200
    assert resp.json()["authenticated"] is True


def test_dev_get_session_invalid_token(monkeypatch, client):
    import services.api.main as main_mod
    monkeypatch.setattr(main_mod, "DEV_MODE", True)
    resp = client.get("/api/v1/dev/session?token=badtoken")
    assert resp.json()["authenticated"] is False


def test_analysis_error_stored_on_exception(client):
    """When get_riot_report raises, report.status becomes 'error'."""
    with (
        patch("services.riot.service.get_riot_report",
              new=AsyncMock(side_effect=Exception("Riot API down"))),
    ):
        resp = client.post("/api/v1/analyze", json={"riot_id": "TestPlayer#NA1"})
        assert resp.status_code == 200
        report_id = resp.json()["report_id"]

        import time
        for _ in range(10):
            r = client.get(f"/api/v1/report/{report_id}")
            if r.json()["status"] in ("error", "done"):
                break
            time.sleep(0.1)

        result = client.get(f"/api/v1/report/{report_id}").json()
        assert result["status"] == "error"
        assert "Riot API down" in (result["error"] or "")
