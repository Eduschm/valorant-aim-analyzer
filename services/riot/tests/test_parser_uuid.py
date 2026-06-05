"""Gate tests for UUID resolution in the parser — no network calls."""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
import services.riot.uuid_map as uuid_map
from services.riot.parser import parse_match, build_riot_report
from contracts.schemas import MatchStat

PUUID = "test-puuid-parser-uuid"

JETT_UUID   = "jett-test-uuid"
VANDAL_UUID = "vandal-test-uuid"

FIXTURE_MATCH = {
    "matchInfo": {"matchId": "match-uuid-test", "numberOfRounds": 20},
    "players": [{
        "puuid": PUUID,
        "teamId": "Red",
        "characterId": JETT_UUID,
        "stats": {
            "kills": 15, "deaths": 10, "assists": 3,
            "headshots": 8, "bodyshots": 20, "legshots": 4,
            "score": 2800,
        },
    }],
    "teams": [{"teamId": "Red", "won": True}],
    "roundResults": [
        {"playerStats": [
            {"puuid": PUUID, "kills": [
                {"finishingDamage": {"damageItem": VANDAL_UUID}},
                {"finishingDamage": {"damageItem": VANDAL_UUID}},
            ]}
        ]}
    ],
}


@pytest.fixture(autouse=True)
def mock_uuid_maps(monkeypatch):
    """Inject known UUID maps; prevent any network calls during tests."""
    monkeypatch.setattr(uuid_map, "_agent_map",  {JETT_UUID: "Jett", JETT_UUID.lower(): "Jett"})
    monkeypatch.setattr(uuid_map, "_weapon_map", {VANDAL_UUID: "Vandal", VANDAL_UUID.lower(): "Vandal"})
    monkeypatch.setattr(uuid_map, "_maps_loaded", True)


def test_parse_match_resolves_agent_uuid():
    """parse_match returns human agent name, not UUID."""
    stat = parse_match(FIXTURE_MATCH, PUUID)
    assert stat is not None
    assert stat.agent == "Jett"


def test_parse_match_resolves_weapon_uuid():
    """parse_match resolves weapon UUID from round results to display name."""
    stat = parse_match(FIXTURE_MATCH, PUUID)
    assert stat is not None
    assert stat.weapon == "Vandal"


def test_parse_match_unknown_uuid_passthrough():
    """Unknown UUIDs pass through unchanged (no crash, no empty string)."""
    match = {
        **FIXTURE_MATCH,
        "players": [{
            **FIXTURE_MATCH["players"][0],
            "characterId": "totally-unknown-uuid",
        }],
        "roundResults": [],
    }
    stat = parse_match(match, PUUID)
    assert stat is not None
    assert stat.agent == "totally-unknown-uuid"  # passthrough on miss


def test_build_riot_report_stores_region():
    """build_riot_report propagates region to RiotReport."""
    matches = [MatchStat("m1", "Jett", "Vandal", 10, 8, 2, 20.0, 130.0, True)]
    report = build_riot_report(
        puuid="p", game_name="Test", tag_line="EU1",
        matches=matches, rank_data={"rank": "Gold 2", "rank_delta": 5},
        region="eu",
    )
    assert report.region == "eu"


def test_build_riot_report_default_region():
    """build_riot_report defaults region to 'na' when not specified."""
    report = build_riot_report(
        puuid="p", game_name="T", tag_line="NA1",
        matches=[], rank_data={"rank": "Unranked", "rank_delta": 0},
    )
    assert report.region == "na"
