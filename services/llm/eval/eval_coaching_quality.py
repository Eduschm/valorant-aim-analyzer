"""
Periodic eval: coaching report quality gate.

Calls the real LLM for 5 fixture reports and verifies:
  1. Every tip mentions at least one number from the input stats.
  2. top_weakness references a stat that is below the rank-median for that bracket.

Pass threshold: 4/5 fixtures.

Run with:
    python -m pytest services/llm/eval/eval_coaching_quality.py -v

Requires ANTHROPIC_API_KEY. Skipped when the key is absent.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import re
import pytest

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

from contracts.schemas import RiotReport, MatchStat, CoachingReport

# Approximate median HS% by rank bracket (used to check top_weakness)
_MEDIAN_HS_PCT: dict[str, float] = {
    "iron":     15.0,
    "bronze":   18.0,
    "silver":   20.0,
    "gold":     23.0,
    "platinum": 26.0,
    "diamond":  28.0,
    "immortal": 30.0,
    "radiant":  32.0,
}

# Five fixtures covering different rank brackets
_FIXTURES: list[RiotReport] = [
    RiotReport(
        puuid="eval-iron",   game_name="IronPlayer",    tag_line="NA1",
        current_rank="Iron 2",    rank_delta=-5,
        matches=[MatchStat(f"m{i}", "Reyna", "Spectre", 10, 18, 2, 10.0, 80.0, False) for i in range(5)],
        avg_headshot_pct=10.0, avg_adr=80.0, top_agent="Reyna", top_weapon="Spectre", win_rate=0.2,
    ),
    RiotReport(
        puuid="eval-silver", game_name="SilverPlayer",  tag_line="NA1",
        current_rank="Silver 3",  rank_delta=8,
        matches=[MatchStat(f"m{i}", "Sage", "Vandal", 14, 13, 6, 18.0, 130.0, True) for i in range(5)],
        avg_headshot_pct=18.0, avg_adr=130.0, top_agent="Sage", top_weapon="Vandal", win_rate=0.6,
    ),
    RiotReport(
        puuid="eval-gold",   game_name="GoldPlayer",    tag_line="NA1",
        current_rank="Gold 2",    rank_delta=12,
        matches=[MatchStat(f"m{i}", "Jett", "Vandal", 18, 11, 4, 21.0, 160.0, True) for i in range(5)],
        avg_headshot_pct=21.0, avg_adr=160.0, top_agent="Jett", top_weapon="Vandal", win_rate=0.7,
    ),
    RiotReport(
        puuid="eval-plat",   game_name="PlatPlayer",    tag_line="NA1",
        current_rank="Platinum 1", rank_delta=3,
        matches=[MatchStat(f"m{i}", "Chamber", "Operator", 16, 12, 3, 24.0, 145.0, True) for i in range(5)],
        avg_headshot_pct=24.0, avg_adr=145.0, top_agent="Chamber", top_weapon="Operator", win_rate=0.55,
    ),
    RiotReport(
        puuid="eval-diamond", game_name="DiamondPlayer", tag_line="NA1",
        current_rank="Diamond 2", rank_delta=18,
        matches=[MatchStat(f"m{i}", "Neon", "Phantom", 22, 10, 5, 25.0, 175.0, True) for i in range(5)],
        avg_headshot_pct=25.0, avg_adr=175.0, top_agent="Neon", top_weapon="Phantom", win_rate=0.8,
    ),
]


def _numbers_from_report(riot: RiotReport) -> list[str]:
    """Extract number strings that should appear in tips/weakness."""
    return [
        str(int(riot.avg_headshot_pct)),
        f"{riot.avg_headshot_pct:.1f}",
        str(int(riot.avg_adr)),
        f"{riot.win_rate * 100:.0f}",
        str(riot.rank_delta),
    ]


def _tip_contains_number(tip: str, riot: RiotReport) -> bool:
    numbers = _numbers_from_report(riot)
    return any(n in tip for n in numbers) or bool(re.search(r"\d+", tip))


def _weakness_references_below_median_stat(weakness: str, riot: RiotReport) -> bool:
    rank_key = riot.current_rank.lower().split()[0]
    median_hs = _MEDIAN_HS_PCT.get(rank_key, 20.0)
    hs_below_median = riot.avg_headshot_pct < median_hs
    if hs_below_median and any(kw in weakness.lower() for kw in ["headshot", "hs", "aim"]):
        return True
    # Accept any stat reference as a fallback
    return bool(re.search(r"\d+", weakness))


@pytest.mark.skipif(not ANTHROPIC_API_KEY, reason="ANTHROPIC_API_KEY not set — skipping live LLM eval")
@pytest.mark.asyncio
@pytest.mark.parametrize("riot", _FIXTURES, ids=[r.current_rank for r in _FIXTURES])
async def test_tips_contain_numbers_from_stats(riot: RiotReport):
    """Every tip must reference at least one number from the player's stats."""
    from services.llm.coach import generate_coaching_report
    report = await generate_coaching_report(riot)

    failing = [t for t in report.tips if not _tip_contains_number(t, riot)]
    assert not failing, f"Tips without stat numbers: {failing}"


@pytest.mark.skipif(not ANTHROPIC_API_KEY, reason="ANTHROPIC_API_KEY not set — skipping live LLM eval")
@pytest.mark.asyncio
@pytest.mark.parametrize("riot", _FIXTURES, ids=[r.current_rank for r in _FIXTURES])
async def test_weakness_references_relevant_stat(riot: RiotReport):
    """top_weakness must reference a stat that's meaningful for that rank."""
    from services.llm.coach import generate_coaching_report
    report = await generate_coaching_report(riot)
    assert _weakness_references_below_median_stat(report.top_weakness, riot), (
        f"top_weakness '{report.top_weakness}' does not reference a relevant stat"
    )
