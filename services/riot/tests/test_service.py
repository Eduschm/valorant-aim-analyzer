"""Tests for get_riot_report() orchestration — mocked client."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from contracts.schemas import RiotReport
from services.riot.client import RiotAPIError


PUUID = "test-puuid-xyz"

MOCK_MATCH = {
    "matchInfo": {"matchId": "m1", "numberOfRounds": 20},
    "players": [{
        "puuid": PUUID, "teamId": "Red", "characterId": "jett",
        "competitiveTier": 13,
        "stats": {"kills": 18, "deaths": 12, "assists": 3,
                  "headshots": 10, "bodyshots": 25, "legshots": 5, "score": 3200},
    }],
    "teams": [{"teamId": "Red", "won": True}],
    "roundResults": [],
}

MOCK_MATCH_UNRANKED = {
    **MOCK_MATCH,
    "players": [{k: v for k, v in MOCK_MATCH["players"][0].items() if k != "competitiveTier"}],
}


@pytest.mark.asyncio
async def test_get_riot_report_full_pipeline(monkeypatch):
    monkeypatch.setenv("MATCH_PROVIDER", "riot")
    with patch("services.riot.service.RiotClient") as MockClient:
        inst = MockClient.return_value.__aenter__.return_value
        inst.get_puuid      = AsyncMock(return_value=PUUID)
        inst.get_match_ids  = AsyncMock(return_value=["m1", "m2"])
        inst.get_match      = AsyncMock(return_value=MOCK_MATCH)

        from services.riot.service import get_riot_report
        report = await get_riot_report("TestPlayer#NA1")

    assert isinstance(report, RiotReport)
    assert report.game_name == "TestPlayer"
    assert report.tag_line  == "NA1"
    assert report.puuid     == PUUID
    # rank derived from Riot competitiveTier (13 -> Gold 2); same tier both matches -> delta 0
    assert report.current_rank == "Gold 2"
    assert report.rank_delta   == 0
    assert len(report.matches) == 2   # both matches parsed


@pytest.mark.asyncio
async def test_get_riot_report_invalid_format_raises():
    from services.riot.service import get_riot_report
    with pytest.raises(ValueError, match="Invalid Riot ID"):
        await get_riot_report("NoHashHere")


@pytest.mark.asyncio
async def test_get_riot_report_skips_failed_matches(monkeypatch):
    """One match fetch fails — rest should still succeed."""
    monkeypatch.setenv("MATCH_PROVIDER", "riot")
    with patch("services.riot.service.RiotClient") as MockClient:
        inst = MockClient.return_value.__aenter__.return_value
        inst.get_puuid     = AsyncMock(return_value=PUUID)
        inst.get_match_ids = AsyncMock(return_value=["m1", "m2", "m3"])
        # m2 raises, m1 and m3 succeed
        inst.get_match     = AsyncMock(side_effect=[
            MOCK_MATCH,
            RiotAPIError(404, "not found"),
            MOCK_MATCH,
        ])

        from services.riot.service import get_riot_report
        report = await get_riot_report("TestPlayer#NA1")

    assert len(report.matches) == 2


@pytest.mark.asyncio
async def test_get_riot_report_rank_unranked_without_tier(monkeypatch):
    """Matches without competitiveTier → rank shown as Unranked, report still succeeds."""
    monkeypatch.setenv("MATCH_PROVIDER", "riot")
    with patch("services.riot.service.RiotClient") as MockClient:
        inst = MockClient.return_value.__aenter__.return_value
        inst.get_puuid     = AsyncMock(return_value=PUUID)
        inst.get_match_ids = AsyncMock(return_value=["m1"])
        inst.get_match     = AsyncMock(return_value=MOCK_MATCH_UNRANKED)

        from services.riot.service import get_riot_report
        report = await get_riot_report("TestPlayer#NA1")

    assert report.current_rank == "Unranked"
    assert report.rank_delta   == 0
