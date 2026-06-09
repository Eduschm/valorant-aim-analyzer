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


# ------------------------------------------------------------------ #
# Region passthrough
# ------------------------------------------------------------------ #

def test_region_defaults_to_na(client):
    """Omitting region defaults to 'na' and is passed to get_riot_report."""
    captured = {}

    async def fake_report(riot_id, region="na", match_count=20):
        captured["region"] = region
        return MOCK_RIOT_REPORT

    with (
        patch("services.riot.service.get_riot_report", new=fake_report),
        patch("services.llm.coach.generate_coaching_report", new=AsyncMock(return_value=MOCK_COACHING)),
    ):
        resp = client.post("/api/v1/analyze", json={"riot_id": "TestPlayer#NA1"})
        assert resp.status_code == 200
        report_id = resp.json()["report_id"]
        import time
        for _ in range(10):
            if client.get(f"/api/v1/report/{report_id}").json()["status"] in ("done", "error"):
                break
            time.sleep(0.1)
    assert captured.get("region") == "na"


def test_region_passed_through(client):
    """Selected region is forwarded to get_riot_report, lowercased."""
    captured = {}

    async def fake_report(riot_id, region="na", match_count=20):
        captured["region"] = region
        return MOCK_RIOT_REPORT

    with (
        patch("services.riot.service.get_riot_report", new=fake_report),
        patch("services.llm.coach.generate_coaching_report", new=AsyncMock(return_value=MOCK_COACHING)),
    ):
        resp = client.post("/api/v1/analyze", json={"riot_id": "TestPlayer#EUW", "region": "EU"})
        assert resp.status_code == 200
        report_id = resp.json()["report_id"]
        import time
        for _ in range(10):
            if client.get(f"/api/v1/report/{report_id}").json()["status"] in ("done", "error"):
                break
            time.sleep(0.1)
    assert captured.get("region") == "eu"


def test_invalid_region_rejected(client):
    resp = client.post("/api/v1/analyze", json={"riot_id": "Name#TAG", "region": "zz"})
    assert resp.status_code == 422


# ------------------------------------------------------------------ #
# Friendly error mapping
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("status,needle", [
    (401, "invalid or expired"),
    (403, "does not have Valorant access"),
    (404, "Player not found"),
    (429, "rate limit"),
])
def test_friendly_error_maps_riot_status(status, needle):
    from services.api.main import _friendly_error
    from services.riot.client import RiotAPIError
    msg = _friendly_error(RiotAPIError(status, "raw"))
    assert needle.lower() in msg.lower()


def test_friendly_error_falls_back_to_message():
    from services.api.main import _friendly_error
    assert _friendly_error(ValueError("boom")) == "boom"


# ------------------------------------------------------------------ #
# Rate limiting  (Issue #21)
# ------------------------------------------------------------------ #

def test_rate_limit_allows_first_ten_requests(client):
    """10 requests/minute from the same IP all succeed."""
    from services.api.main import limiter
    limiter._storage.reset()
    for i in range(10):
        r = client.post("/api/v1/analyze", json={"riot_id": f"Player{i}#NA1"})
        assert r.status_code == 200, f"Request {i+1} failed with {r.status_code}"


def test_rate_limit_blocks_on_11th_request(client):
    """11th request within the same window returns 429 with Retry-After."""
    from services.api.main import limiter
    limiter._storage.reset()
    for i in range(10):
        client.post("/api/v1/analyze", json={"riot_id": f"Player{i}#NA1"})
    r = client.post("/api/v1/analyze", json={"riot_id": "Player10#NA1"})
    assert r.status_code == 429
    assert "retry-after" in {k.lower() for k in r.headers}


def test_rate_limit_does_not_affect_other_endpoints(client):
    """GET /health is never rate-limited."""
    from services.api.main import limiter
    limiter._storage.reset()
    for _ in range(15):
        r = client.get("/health")
        assert r.status_code == 200


def test_friendly_403_surfaced_in_report(client):
    """A RiotAPIError 403 from the pipeline becomes the actionable VAL message."""
    from services.riot.client import RiotAPIError
    with patch("services.riot.service.get_riot_report",
               new=AsyncMock(side_effect=RiotAPIError(403, "Forbidden"))):
        resp = client.post("/api/v1/analyze", json={"riot_id": "TestPlayer#NA1"})
        report_id = resp.json()["report_id"]
        import time
        for _ in range(10):
            if client.get(f"/api/v1/report/{report_id}").json()["status"] in ("error", "done"):
                break
            time.sleep(0.1)
        result = client.get(f"/api/v1/report/{report_id}").json()
    assert result["status"] == "error"
    assert "Valorant access" in (result["error"] or "")
