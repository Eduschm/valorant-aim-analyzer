"""Tests for get_riot_report() orchestration — mocked client."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from contracts.schemas import RiotReport
from services.riot.client import RiotAPIError

PUUID = "test-puuid-xyz"

MOCK_MATCH = {
    "matchInfo": {"matchId": "m1", "numberOfRounds": 20},
    "players": [{
        "puuid": PUUID, "teamId": "Red", "characterId": "jett-uuid",
        "stats": {"kills": 18, "deaths": 12, "assists": 3,
                  "headshots": 10, "bodyshots": 25, "legshots": 5, "score": 3200},
    }],
    "teams": [{"teamId": "Red", "won": True}],
    "roundResults": [],
}

MOCK_RANK = {
    "data": {"current_data": {"currenttierpatched": "Gold 2", "mmr_change_to_last_game": 15}}
}

# Empty name maps — UUIDs pass through unchanged
EMPTY_AGENT_NAMES:  dict = {}
EMPTY_WEAPON_NAMES: dict = {}


def _patch_names(agent_names=None, weapon_names=None):
    """Return a pair of patches for get_agent_names / get_weapon_names."""
    return (
        patch("services.riot.service.get_agent_names",  AsyncMock(return_value=agent_names  or EMPTY_AGENT_NAMES)),
        patch("services.riot.service.get_weapon_names", AsyncMock(return_value=weapon_names or EMPTY_WEAPON_NAMES)),
    )


@pytest.mark.asyncio
async def test_get_riot_report_full_pipeline():
    p_agents, p_weapons = _patch_names()
    with patch("services.riot.service.RiotClient") as MockClient, p_agents, p_weapons:
        inst = MockClient.return_value.__aenter__.return_value
        inst.get_puuid     = AsyncMock(return_value=PUUID)
        inst.get_match_ids = AsyncMock(return_value=["m1", "m2"])
        inst.get_match     = AsyncMock(return_value=MOCK_MATCH)
        inst.get_rank      = AsyncMock(return_value=MOCK_RANK)

        from services.riot.service import get_riot_report
        report = await get_riot_report("TestPlayer#NA1")

    assert isinstance(report, RiotReport)
    assert report.game_name    == "TestPlayer"
    assert report.tag_line     == "NA1"
    assert report.puuid        == PUUID
    assert report.current_rank == "Gold 2"
    assert report.rank_delta   == 15
    assert len(report.matches) == 2
    assert report.region       == "na"


@pytest.mark.asyncio
async def test_get_riot_report_invalid_format_raises():
    from services.riot.service import get_riot_report
    with pytest.raises(ValueError, match="Invalid Riot ID"):
        await get_riot_report("NoHashHere")


@pytest.mark.asyncio
async def test_get_riot_report_skips_failed_matches():
    """One match fetch fails — rest should still succeed."""
    p_agents, p_weapons = _patch_names()
    with patch("services.riot.service.RiotClient") as MockClient, p_agents, p_weapons:
        inst = MockClient.return_value.__aenter__.return_value
        inst.get_puuid     = AsyncMock(return_value=PUUID)
        inst.get_match_ids = AsyncMock(return_value=["m1", "m2", "m3"])
        inst.get_match     = AsyncMock(side_effect=[
            MOCK_MATCH,
            RiotAPIError(404, "not found"),
            MOCK_MATCH,
        ])
        inst.get_rank = AsyncMock(return_value=MOCK_RANK)

        from services.riot.service import get_riot_report
        report = await get_riot_report("TestPlayer#NA1")

    assert len(report.matches) == 2


@pytest.mark.asyncio
async def test_get_riot_report_rank_non_fatal():
    """get_rank returning {} → rank shown as Unranked, report still succeeds."""
    p_agents, p_weapons = _patch_names()
    with patch("services.riot.service.RiotClient") as MockClient, p_agents, p_weapons:
        inst = MockClient.return_value.__aenter__.return_value
        inst.get_puuid     = AsyncMock(return_value=PUUID)
        inst.get_match_ids = AsyncMock(return_value=["m1"])
        inst.get_match     = AsyncMock(return_value=MOCK_MATCH)
        inst.get_rank      = AsyncMock(return_value={})

        from services.riot.service import get_riot_report
        report = await get_riot_report("TestPlayer#NA1")

    assert report.current_rank == "Unranked"
    assert report.rank_delta   == 0


@pytest.mark.asyncio
async def test_region_auto_detection_tries_eu_after_na_404():
    """When na returns 404, the service retries eu and succeeds."""
    p_agents, p_weapons = _patch_names()
    with patch("services.riot.service.RiotClient") as MockClient, p_agents, p_weapons:
        inst = MockClient.return_value.__aenter__.return_value
        # First call (na) raises 404; second call (eu) succeeds
        inst.get_puuid = AsyncMock(side_effect=[
            RiotAPIError(404, "not found"),
            PUUID,
        ])
        inst.get_match_ids = AsyncMock(return_value=["m1"])
        inst.get_match     = AsyncMock(return_value=MOCK_MATCH)
        inst.get_rank      = AsyncMock(return_value=MOCK_RANK)

        from services.riot.service import get_riot_report
        report = await get_riot_report("EuPlayer#EU1")

    assert report.region == "eu"
    assert len(report.matches) == 1


@pytest.mark.asyncio
async def test_region_auto_detection_all_fail_raises():
    """If all candidate regions fail with 404, RiotAPIError is raised."""
    p_agents, p_weapons = _patch_names()
    with patch("services.riot.service.RiotClient") as MockClient, p_agents, p_weapons:
        inst = MockClient.return_value.__aenter__.return_value
        inst.get_puuid = AsyncMock(side_effect=RiotAPIError(404, "not found"))

        from services.riot.service import get_riot_report
        with pytest.raises(RiotAPIError) as exc:
            await get_riot_report("Ghost#0000")

    assert exc.value.status == 404


@pytest.mark.asyncio
async def test_explicit_region_bypasses_auto_detection():
    """Passing region explicitly uses only that region."""
    p_agents, p_weapons = _patch_names()
    with patch("services.riot.service.RiotClient") as MockClient, p_agents, p_weapons:
        inst = MockClient.return_value.__aenter__.return_value
        inst.get_puuid     = AsyncMock(return_value=PUUID)
        inst.get_match_ids = AsyncMock(return_value=[])
        inst.get_match     = AsyncMock(return_value=MOCK_MATCH)
        inst.get_rank      = AsyncMock(return_value={})

        from services.riot.service import get_riot_report
        report = await get_riot_report("Player#AP1", region="ap")

    assert report.region == "ap"
    # Only one RiotClient instantiation with "ap"
    MockClient.assert_called_once_with("ap")


@pytest.mark.asyncio
async def test_name_resolution_replaces_uuids():
    """Agent/weapon UUIDs are replaced with human names when maps are provided."""
    agent_map  = {"jett-uuid": "Jett"}
    weapon_map = {"vandal-uuid": "Vandal"}
    p_agents, p_weapons = _patch_names(agent_map, weapon_map)

    match_with_uuids = {
        **MOCK_MATCH,
        "players": [{
            **MOCK_MATCH["players"][0],
            "characterId": "jett-uuid",
        }],
        "roundResults": [{"playerStats": [{"puuid": PUUID, "kills": [
            {"finishingDamage": {"damageItem": "vandal-uuid"}}
        ]}]}],
    }

    with patch("services.riot.service.RiotClient") as MockClient, p_agents, p_weapons:
        inst = MockClient.return_value.__aenter__.return_value
        inst.get_puuid     = AsyncMock(return_value=PUUID)
        inst.get_match_ids = AsyncMock(return_value=["m1"])
        inst.get_match     = AsyncMock(return_value=match_with_uuids)
        inst.get_rank      = AsyncMock(return_value=MOCK_RANK)

        from services.riot.service import get_riot_report
        report = await get_riot_report("Player#NA1")

    assert report.matches[0].agent  == "Jett"
    assert report.matches[0].weapon == "Vandal"
    assert report.top_agent  == "Jett"
    assert report.top_weapon == "Vandal"
