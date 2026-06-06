"""Tests for get_riot_report() Henrik provider path + provider selection."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from unittest.mock import AsyncMock, patch

from contracts.schemas import RiotReport

PUUID = "p-tenz"

HENRIK_MATCH = {
    "metadata": {"match_id": "m1"},
    "players": [{
        "puuid": PUUID, "team_id": "Red",
        "agent": {"name": "Jett"}, "tier": {"id": 13, "name": "Gold 2"},
        "stats": {"kills": 20, "deaths": 12, "assists": 4,
                  "headshots": 30, "bodyshots": 60, "legshots": 10,
                  "score": 4200, "damage": {"dealt": 3600}},
    }],
    "teams": [{"team_id": "Red", "won": True, "rounds": {"won": 13, "lost": 7}}],
    "rounds": [{} for _ in range(20)],
    "kills": [{"killer": {"puuid": PUUID}, "weapon": {"name": "Vandal"}}],
}

HENRIK_MMR = {"current": {"tier": {"id": 13, "name": "Gold 2"}, "rr": 42}}


def test_provider_defaults_to_henrik_when_key_present(monkeypatch):
    from services.riot import service
    monkeypatch.delenv("MATCH_PROVIDER", raising=False)
    monkeypatch.setattr(service, "HENRIK_API_KEY", "key-123")
    assert service._resolve_provider() == "henrik"


def test_provider_defaults_to_riot_without_key(monkeypatch):
    from services.riot import service
    monkeypatch.delenv("MATCH_PROVIDER", raising=False)
    monkeypatch.setattr(service, "HENRIK_API_KEY", "")
    assert service._resolve_provider() == "riot"


def test_explicit_provider_overrides(monkeypatch):
    from services.riot import service
    monkeypatch.setenv("MATCH_PROVIDER", "riot")
    monkeypatch.setattr(service, "HENRIK_API_KEY", "key-123")
    assert service._resolve_provider() == "riot"


@pytest.mark.asyncio
async def test_get_riot_report_henrik_pipeline(monkeypatch):
    monkeypatch.setenv("MATCH_PROVIDER", "henrik")
    with patch("services.riot.service.HenrikClient") as MockClient:
        inst = MockClient.return_value.__aenter__.return_value
        inst.get_account = AsyncMock(return_value={"puuid": PUUID})
        inst.get_matches = AsyncMock(return_value=[HENRIK_MATCH, HENRIK_MATCH])
        inst.get_mmr = AsyncMock(return_value=HENRIK_MMR)

        from services.riot.service import get_riot_report
        report = await get_riot_report("TenZ#0505", region="na")

    assert isinstance(report, RiotReport)
    assert report.puuid == PUUID
    assert report.game_name == "TenZ" and report.tag_line == "0505"
    assert report.current_rank == "Gold 2"
    assert report.top_agent == "Jett"
    assert report.top_weapon == "Vandal"
    assert report.avg_adr == 180.0
    assert report.win_rate == 1.0
    assert len(report.matches) == 2


@pytest.mark.asyncio
async def test_henrik_pipeline_survives_mmr_failure(monkeypatch):
    """MMR failure is non-fatal — rank derived from match tiers, report still built."""
    monkeypatch.setenv("MATCH_PROVIDER", "henrik")
    from services.riot.henrik_client import HenrikAPIError
    with patch("services.riot.service.HenrikClient") as MockClient:
        inst = MockClient.return_value.__aenter__.return_value
        inst.get_account = AsyncMock(return_value={"puuid": PUUID})
        inst.get_matches = AsyncMock(return_value=[HENRIK_MATCH])
        inst.get_mmr = AsyncMock(side_effect=HenrikAPIError(429, "rate limited"))

        from services.riot.service import get_riot_report
        report = await get_riot_report("TenZ#0505", region="na")

    assert report.current_rank == "Gold 2"   # derived from match tier id 13
    assert len(report.matches) == 1


@pytest.mark.asyncio
async def test_get_riot_report_invalid_format_raises():
    from services.riot.service import get_riot_report
    with pytest.raises(ValueError, match="Invalid Riot ID"):
        await get_riot_report("NoHashHere")
