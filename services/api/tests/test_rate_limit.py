"""Gate tests for the /api/v1/analyze rate limit (10/minute)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from contracts.schemas import RiotReport, CoachingReport, MatchStat


MOCK_RIOT = RiotReport(
    puuid="p", game_name="RLPlayer", tag_line="EU",
    current_rank="Gold 1", rank_delta=0,
    matches=[MatchStat("m1", "Jett", "Vandal", 10, 8, 2, 22.0, 130.0, True)],
    avg_headshot_pct=22.0, avg_adr=130.0,
    top_agent="Jett", top_weapon="Vandal", win_rate=0.5,
)
MOCK_COACHING = CoachingReport(
    summary="Good.", top_weakness="HS% low.",
    tips=["tip1"], encouragement="Keep going.", raw_response="{}",
)


@pytest.fixture
def rate_client():
    """Fresh TestClient with a reset rate-limit storage."""
    from services.api.store import store
    store._reports.clear()
    from services.api.main import app, limiter
    # Reset the in-memory bucket so prior tests don't consume our allowance.
    limiter._limiter.storage.reset()
    return TestClient(app)


def test_rate_limit_header_present(rate_client):
    """X-RateLimit-Limit header should appear on the analyze endpoint."""
    with (
        patch("services.riot.service.get_riot_report", new=AsyncMock(return_value=MOCK_RIOT)),
        patch("services.llm.coach.generate_coaching_report", new=AsyncMock(return_value=MOCK_COACHING)),
    ):
        resp = rate_client.post("/api/v1/analyze", json={"riot_id": "RLPlayer#EU"})
    assert resp.status_code == 200
    assert "x-ratelimit-limit" in {k.lower() for k in resp.headers}


def test_rate_limit_429_on_11th_request(rate_client):
    """The 11th request within a minute must return 429."""
    with (
        patch("services.riot.service.get_riot_report", new=AsyncMock(return_value=MOCK_RIOT)),
        patch("services.llm.coach.generate_coaching_report", new=AsyncMock(return_value=MOCK_COACHING)),
    ):
        for _ in range(10):
            r = rate_client.post("/api/v1/analyze", json={"riot_id": "RLPlayer#EU"})
            assert r.status_code == 200, f"Expected 200 but got {r.status_code}"
        over_limit = rate_client.post("/api/v1/analyze", json={"riot_id": "RLPlayer#EU"})
    assert over_limit.status_code == 429


def test_rate_limit_429_body_is_json(rate_client):
    """429 response must be parseable JSON."""
    with (
        patch("services.riot.service.get_riot_report", new=AsyncMock(return_value=MOCK_RIOT)),
        patch("services.llm.coach.generate_coaching_report", new=AsyncMock(return_value=MOCK_COACHING)),
    ):
        for _ in range(10):
            rate_client.post("/api/v1/analyze", json={"riot_id": "RLPlayer#EU"})
        resp = rate_client.post("/api/v1/analyze", json={"riot_id": "RLPlayer#EU"})
    assert resp.status_code == 429
    body = resp.json()
    assert "error" in body or "detail" in body
