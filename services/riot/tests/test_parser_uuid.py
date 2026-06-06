"""Gate tests: parser resolves UUIDs → names and computes real ADR."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
import services.riot.uuid_map as uuid_mod
from services.riot.parser import parse_match, build_riot_report
from contracts.schemas import MatchStat


PUUID = "test-puuid-uuid-parser"

JETT_UUID   = "add6443a-41bd-e414-f6ad-e58d267f4e95"
VANDAL_UUID = "9c82e19d-4575-0200-1a81-3eacf00cf872"


@pytest.fixture(autouse=True)
def inject_maps():
    """Inject known UUIDs into the map so parser can resolve them."""
    uuid_mod._agent_map  = {JETT_UUID.lower(): "Jett"}
    uuid_mod._weapon_map = {VANDAL_UUID.lower(): "Vandal"}
    uuid_mod._maps_loaded = True
    yield
    uuid_mod._agent_map   = {}
    uuid_mod._weapon_map  = {}
    uuid_mod._maps_loaded = False


MATCH_WITH_UUID = {
    "matchInfo": {"matchId": "m1", "numberOfRounds": 20},
    "players": [{
        "puuid": PUUID, "teamId": "Red",
        "characterId": JETT_UUID,
        "competitiveTier": 13,
        "stats": {"kills": 10, "deaths": 8, "assists": 2,
                  "headshots": 5, "bodyshots": 10, "legshots": 1, "score": 2000},
    }],
    "teams": [{"teamId": "Red", "won": True}],
    "roundResults": [
        {"playerStats": [
            {"puuid": PUUID, "damage": [{"damage": 100, "receiver": "other"}],
             "kills": [{"finishingDamage": {"damageItem": VANDAL_UUID}}]},
        ]},
        {"playerStats": [
            {"puuid": PUUID, "damage": [{"damage": 80, "receiver": "other2"}],
             "kills": []},
        ]},
    ],
}


def test_agent_uuid_resolved_to_name():
    stat = parse_match(MATCH_WITH_UUID, PUUID)
    assert stat is not None
    assert stat.agent == "Jett"


def test_weapon_uuid_resolved_to_name():
    stat = parse_match(MATCH_WITH_UUID, PUUID)
    assert stat is not None
    assert stat.weapon == "Vandal"


def test_unknown_agent_uuid_falls_back_to_uuid():
    match = {**MATCH_WITH_UUID, "players": [{
        **MATCH_WITH_UUID["players"][0],
        "characterId": "unknown-agent-uuid",
    }]}
    stat = parse_match(match, PUUID)
    assert stat.agent == "unknown-agent-uuid"


def test_real_adr_from_round_results():
    # 2 rounds, 100 + 80 damage = 180 total, 20 rounds → 180/20 = 9.0
    stat = parse_match(MATCH_WITH_UUID, PUUID)
    assert stat is not None
    assert stat.adr == round(180 / 20, 1)
    assert stat.adr_is_estimated is False


def test_adr_estimated_when_no_damage_data():
    match = {
        "matchInfo": {"matchId": "m2", "numberOfRounds": 20},
        "players": [{
            "puuid": PUUID, "teamId": "Blue",
            "characterId": JETT_UUID, "competitiveTier": 13,
            "stats": {"kills": 10, "deaths": 8, "assists": 2,
                      "headshots": 5, "bodyshots": 10, "legshots": 1, "score": 2000},
        }],
        "teams": [{"teamId": "Blue", "won": False}],
        "roundResults": [],  # no round data → fall back to approximation
    }
    stat = parse_match(match, PUUID)
    assert stat.adr == round(2000 / 20, 1)   # 100.0 from score/rounds
    assert stat.adr_is_estimated is True


def test_build_riot_report_adr_estimated_flag_propagates():
    matches = [
        MatchStat("m1", "Jett", "Vandal", 10, 8, 2, 25.0, 100.0, True, adr_is_estimated=True),
        MatchStat("m2", "Jett", "Vandal", 12, 7, 3, 28.0, 130.0, True, adr_is_estimated=False),
    ]
    report = build_riot_report("p", "Player", "TAG", matches, {"rank": "Gold 1", "rank_delta": 0})
    assert report.adr_is_estimated is True  # any() → True when at least one is estimated
