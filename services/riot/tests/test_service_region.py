"""Gate tests for region auto-detection in get_riot_report."""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from contracts.schemas import RiotReport
from services.riot.client import RiotAPIError


PUUID = "test-puuid-region"

MOCK_MATCH = {
    "matchInfo": {"matchId": "r1", "numberOfRounds": 20},
    "players": [{
        "puuid": PUUID, "teamId": "Red", "characterId": "jett",
        "stats": {"kills": 12, "deaths": 10, "assists": 4,
                  "headshots": 5, "bodyshots": 20, "legshots": 5, "score": 2400},
    }],
    "teams": [{"teamId": "Red", "won": True}],
    "roundResults": [],
}

MOCK_RANK = {
    "data": {"current_data": {"currenttierpatched": "Silver 1", "mmr_change_to_last_game": 5}}
}


def _make_client_mock(puuid_return=None, puuid_side_effect=None):
    inst = MagicMock()
    if puuid_side_effect:
        inst.get_puuid     = AsyncMock(side_effect=puuid_side_effect)
    else:
        inst.get_puuid     = AsyncMock(return_value=puuid_return)
    inst.get_match_ids = AsyncMock(return_value=["r1"])
    inst.get_match     = AsyncMock(return_value=MOCK_MATCH)
    inst.get_rank      = AsyncMock(return_value=MOCK_RANK)
    inst.__aenter__    = AsyncMock(return_value=inst)
    inst.__aexit__     = AsyncMock(return_value=False)
    return inst


@pytest.mark.asyncio
async def test_region_resolved_in_report():
    """Resolved region is stored in RiotReport.region."""
    with patch("services.riot.service.RiotClient") as MockClient, \
         patch("services.riot.service._build_redis_client", AsyncMock(return_value=None)):
        inst = _make_client_mock(puuid_return=PUUID)
        MockClient.return_value = inst

        from services.riot.service import get_riot_report
        report = await get_riot_report("TestPlayer#NA1", region="eu")

    assert isinstance(report, RiotReport)
    assert report.region == "eu"


@pytest.mark.asyncio
async def test_auto_detect_falls_through_to_eu():
    """When NA returns 404, service retries EU and succeeds."""
    probe_count = {"n": 0}

    def mock_client_factory(region, redis_client=None):
        """Return different mocks per region call order."""
        probe_count["n"] += 1
        if probe_count["n"] == 1:
            # First probe (na) — PUUID raises 404
            inst = _make_client_mock(puuid_side_effect=RiotAPIError(404, "not found"))
        else:
            # Second probe (eu) and subsequent calls — PUUID succeeds
            inst = _make_client_mock(puuid_return=PUUID)
        return inst

    with patch("services.riot.service.RiotClient", side_effect=mock_client_factory), \
         patch("services.riot.service._build_redis_client", AsyncMock(return_value=None)):

        from services.riot.service import get_riot_report
        report = await get_riot_report("EUPlayer#EU1")

    # Should succeed even though NA probe failed
    assert isinstance(report, RiotReport)


@pytest.mark.asyncio
async def test_all_regions_fail_raises():
    """get_riot_report raises RiotAPIError when all probes return 404."""
    with patch("services.riot.service.RiotClient") as MockClient, \
         patch("services.riot.service._build_redis_client", AsyncMock(return_value=None)):
        inst = _make_client_mock(puuid_side_effect=RiotAPIError(404, "not found"))
        MockClient.return_value = inst

        from services.riot.service import get_riot_report
        with pytest.raises(RiotAPIError) as exc_info:
            await get_riot_report("Ghost#0000")

    assert exc_info.value.status == 404


@pytest.mark.asyncio
async def test_non_404_error_propagates_immediately():
    """401 (bad API key) stops probing immediately — no fallback to other regions."""
    call_count = {"n": 0}

    def fail_401(*args, **kwargs):
        call_count["n"] += 1
        raise RiotAPIError(401, "invalid key")

    with patch("services.riot.service.RiotClient") as MockClient, \
         patch("services.riot.service._build_redis_client", AsyncMock(return_value=None)):
        inst = _make_client_mock(puuid_side_effect=RiotAPIError(401, "invalid key"))
        MockClient.return_value = inst

        from services.riot.service import get_riot_report
        with pytest.raises(RiotAPIError) as exc_info:
            await get_riot_report("Player#NA1")

    assert exc_info.value.status == 401
    # Only one probe attempted (not all four regions)
    assert MockClient.call_count <= 2  # one for PUUID probe attempt
