"""Gate tests for riot parser — no real API calls."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from services.riot.parser import parse_match, derive_rank, tier_name, build_riot_report
from contracts.schemas import MatchStat


PUUID = "test-puuid-12345"

FIXTURE_MATCH = {
    "matchInfo": {"matchId": "match-abc", "numberOfRounds": 20},
    "players": [
        {
            "puuid": PUUID,
            "teamId": "Red",
            "characterId": "jett-uuid",
            "competitiveTier": 13,
            "stats": {
                "kills": 18, "deaths": 12, "assists": 3,
                "headshots": 10, "bodyshots": 25, "legshots": 5,
                "score": 3200,
            },
        }
    ],
    "teams": [{"teamId": "Red", "won": True}],
    "roundResults": [],
}

FIXTURE_MATCH_NO_PLAYER = {
    "matchInfo": {"matchId": "match-xyz", "numberOfRounds": 20},
    "players": [{"puuid": "other-puuid", "teamId": "Blue", "characterId": "x",
                 "stats": {"kills":0,"deaths":0,"assists":0,"headshots":0,"bodyshots":0,"legshots":0,"score":0}}],
    "teams": [{"teamId": "Blue", "won": False}],
    "roundResults": [],
}


def test_parse_match_basic():
    stat = parse_match(FIXTURE_MATCH, PUUID)
    assert stat is not None
    assert stat.kills == 18
    assert stat.deaths == 12
    assert stat.assists == 3
    assert stat.won is True
    assert stat.match_id == "match-abc"
    assert stat.agent == "jett-uuid"
    assert stat.competitive_tier == 13


def test_parse_match_missing_competitive_tier_defaults_zero():
    match = {**FIXTURE_MATCH,
             "players": [{k: v for k, v in FIXTURE_MATCH["players"][0].items()
                          if k != "competitiveTier"}]}
    stat = parse_match(match, PUUID)
    assert stat.competitive_tier == 0


def test_parse_match_headshot_pct():
    stat = parse_match(FIXTURE_MATCH, PUUID)
    # headshots=10, bodyshots=25, legshots=5 → total=40 → hs%=25%
    assert stat.headshot_pct == 25.0


def test_parse_match_adr():
    stat = parse_match(FIXTURE_MATCH, PUUID)
    # score=3200, rounds=20 → adr=160
    assert stat.adr == 160.0


def test_parse_match_player_not_found():
    stat = parse_match(FIXTURE_MATCH_NO_PLAYER, PUUID)
    assert stat is None


def test_parse_match_zero_shots():
    match = {**FIXTURE_MATCH,
             "players": [{**FIXTURE_MATCH["players"][0],
                          "stats": {**FIXTURE_MATCH["players"][0]["stats"],
                                    "headshots": 0, "bodyshots": 0, "legshots": 0}}]}
    stat = parse_match(match, PUUID)
    assert stat.headshot_pct == 0.0


def test_tier_name_mapping():
    assert tier_name(13) == "Gold 2"
    assert tier_name(27) == "Radiant"
    assert tier_name(0) == "Unranked"
    assert tier_name(99) == "Unranked"   # unmapped tier


def _ranked(tier: int) -> MatchStat:
    return MatchStat("m", "Jett", "Vandal", 1, 1, 1, 0.0, 0.0, True, competitive_tier=tier)


def test_derive_rank_uses_most_recent_match():
    # newest-first: current rank is matches[0]
    matches = [_ranked(14), _ranked(13), _ranked(12)]
    result = derive_rank(matches)
    assert result["rank"] == "Gold 3"
    # climbed from Gold 1 (12) to Gold 3 (14)
    assert result["rank_delta"] == 2


def test_derive_rank_negative_delta():
    matches = [_ranked(12), _ranked(14)]   # dropped from Gold 3 to Gold 1
    result = derive_rank(matches)
    assert result["rank"] == "Gold 1"
    assert result["rank_delta"] == -2


def test_derive_rank_unranked_when_no_tiers():
    matches = [_ranked(0), _ranked(0)]
    result = derive_rank(matches)
    assert result["rank"] == "Unranked"
    assert result["rank_delta"] == 0


def test_derive_rank_empty():
    result = derive_rank([])
    assert result["rank"] == "Unranked"
    assert result["rank_delta"] == 0


def test_build_riot_report_aggregation():
    matches = [
        MatchStat("m1","Jett","Vandal",18,12,3,25.0,160.0,True),
        MatchStat("m2","Jett","Vandal",10,15,5,18.0,120.0,False),
        MatchStat("m3","Sage","Phantom",14,13,8,30.0,140.0,True),
    ]
    report = build_riot_report("puuid","TestPlayer","NA1",matches,{"rank":"Gold 2","rank_delta":5})
    assert report.win_rate == round(2/3, 2)
    assert report.top_agent == "Jett"
    assert report.top_weapon == "Vandal"
    assert report.avg_headshot_pct == round((25+18+30)/3, 1)


def test_build_riot_report_empty_matches():
    report = build_riot_report("p","Name","TAG",[],{"rank":"Unranked","rank_delta":0})
    assert report.total_matches == 0 if hasattr(report, "total_matches") else report.matches == []
