"""Tests for the Henrik v4 match / v3 MMR parser."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from contracts.schemas import MatchStat
from services.riot.henrik_parser import parse_henrik_match, rank_from_mmr


PUUID = "p-tenz"

# A trimmed but shape-accurate Henrik v4 match payload.
MATCH = {
    "metadata": {"match_id": "m1"},
    "players": [
        {
            "puuid": PUUID,
            "team_id": "Red",
            "agent": {"id": "a1", "name": "Jett"},
            "tier": {"id": 13, "name": "Gold 2"},
            "stats": {
                "kills": 20, "deaths": 12, "assists": 4,
                "headshots": 30, "bodyshots": 60, "legshots": 10,
                "score": 4200, "damage": {"dealt": 3600, "received": 2800},
            },
        },
        {"puuid": "other", "team_id": "Blue", "agent": {"name": "Sage"},
         "tier": {"id": 13, "name": "Gold 2"}, "stats": {}},
    ],
    "teams": [
        {"team_id": "Red", "won": True, "rounds": {"won": 13, "lost": 7}},
        {"team_id": "Blue", "won": False, "rounds": {"won": 7, "lost": 13}},
    ],
    "rounds": [{} for _ in range(20)],
    "kills": [
        {"killer": {"puuid": PUUID}, "weapon": {"name": "Vandal"}},
        {"killer": {"puuid": PUUID}, "weapon": {"name": "Vandal"}},
        {"killer": {"puuid": PUUID}, "weapon": {"name": "Operator"}},
        {"killer": {"puuid": "other"}, "weapon": {"name": "Phantom"}},
    ],
}


def test_parse_henrik_match_core_fields():
    stat = parse_henrik_match(MATCH, PUUID)
    assert isinstance(stat, MatchStat)
    assert stat.match_id == "m1"
    assert stat.agent == "Jett"            # human-readable name, not a UUID
    assert stat.kills == 20 and stat.deaths == 12 and stat.assists == 4
    assert stat.won is True
    assert stat.competitive_tier == 13
    assert stat.weapon == "Vandal"         # most-used weapon by kills


def test_parse_henrik_match_adr_and_hs():
    stat = parse_henrik_match(MATCH, PUUID)
    # ADR = damage.dealt / rounds_played = 3600 / 20 = 180.0
    assert stat.adr == 180.0
    # HS% = 30 / (30+60+10) = 30%
    assert stat.headshot_pct == 30.0


def test_parse_henrik_match_rounds_fallback_to_team_rounds():
    match = {**MATCH}
    match = dict(match)
    match.pop("rounds")
    stat = parse_henrik_match(match, PUUID)
    # 13 + 7 = 20 rounds → ADR still 180.0
    assert stat.adr == 180.0


def test_parse_henrik_match_player_absent_returns_none():
    assert parse_henrik_match(MATCH, "not-in-match") is None


def test_rank_from_mmr_prefers_mmr_tier_name():
    mmr = {"current": {"tier": {"id": 13, "name": "Gold 2"}, "rr": 50}}
    matches = [parse_henrik_match(MATCH, PUUID)]
    data = rank_from_mmr(mmr, matches)
    assert data["rank"] == "Gold 2"
    assert data["rank_delta"] == 0


def test_rank_from_mmr_falls_back_to_matches_without_mmr():
    matches = [parse_henrik_match(MATCH, PUUID)]
    data = rank_from_mmr({}, matches)
    assert data["rank"] == "Gold 2"   # derived from match tier id 13


def test_rank_delta_from_match_tiers():
    older = {**MATCH, "players": [{**MATCH["players"][0], "tier": {"id": 11, "name": "Silver 3"}}]}
    newer = parse_henrik_match(MATCH, PUUID)           # tier 13
    oldest = parse_henrik_match(older, PUUID)          # tier 11
    # matches are newest-first → delta = newest(13) - oldest(11) = +2
    data = rank_from_mmr({}, [newer, oldest])
    assert data["rank_delta"] == 2
