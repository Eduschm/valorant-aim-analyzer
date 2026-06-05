"""
Coaching quality eval — periodic, makes real LLM calls.

Run:
    python -m pytest services/llm/eval/ -v

Pass threshold: 4 / 5 fixtures pass all assertions.

Assertions per fixture:
  1. Every tip contains at least one number from the input stats.
  2. top_weakness references a stat that is below median for the player's rank.
"""

from __future__ import annotations

import asyncio
import re
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest

from contracts.schemas import CoachingReport, RiotReport
from services.llm.eval.fixtures import (
    ALL_FIXTURES,
    RANK_MEDIANS,
    get_below_median_stats,
    _kd,
)
from services.llm.coach import generate_coaching_report


# ------------------------------------------------------------------ #
# Assertion helpers                                                    #
# ------------------------------------------------------------------ #

def _numbers_from_report(report: RiotReport) -> list[str]:
    """Extract all numeric strings that appear in the RiotReport."""
    numbers: list[str] = []
    numbers.append(str(round(report.avg_headshot_pct, 1)))
    numbers.append(str(int(report.avg_headshot_pct)))
    numbers.append(str(round(report.avg_adr, 0))[:-2] if ".0" in str(round(report.avg_adr, 0)) else str(round(report.avg_adr, 1)))
    numbers.append(str(int(report.avg_adr)))
    numbers.append(f"{report.win_rate * 100:.0f}")
    numbers.append(str(report.rank_delta).lstrip("+").lstrip("-"))
    kd = _kd(report)
    numbers.append(str(round(kd, 2)))
    numbers.append(str(round(kd, 1)))
    for m in report.matches:
        numbers.extend([str(m.kills), str(m.deaths), str(m.assists)])
        numbers.append(str(int(m.headshot_pct)))
        numbers.append(str(int(m.adr)))
    return [n for n in numbers if n and n != "0"]


def _tip_contains_number(tip: str, numbers: list[str]) -> bool:
    """True if the tip string contains at least one number from the input."""
    tip_numbers = set(re.findall(r"\d+\.?\d*", tip))
    return bool(tip_numbers.intersection(set(numbers)))


def _weakness_references_below_median(weakness: str, report: RiotReport) -> bool:
    """True if top_weakness mentions a stat that is actually below median."""
    below = get_below_median_stats(report)
    if not below:
        return True  # no stat is below median; any weakness is acceptable

    stat_keywords = {
        "hs_pct": ["headshot", "hs%", "hs ", "head"],
        "adr":    ["adr", "damage", "dmg"],
        "kd":     ["k/d", "kd", "kill", "death"],
    }
    weakness_lower = weakness.lower()
    return any(
        any(kw in weakness_lower for kw in stat_keywords.get(stat, []))
        for stat in below
    )


# ------------------------------------------------------------------ #
# Eval tests                                                           #
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
@pytest.mark.parametrize("report", ALL_FIXTURES, ids=[r.current_rank for r in ALL_FIXTURES])
async def test_coaching_quality(report: RiotReport):
    """Every tip references input numbers; top_weakness targets a real below-median stat."""
    coaching: CoachingReport = await generate_coaching_report(report)

    numbers = _numbers_from_report(report)

    # All tips must reference at least one number from the input
    for i, tip in enumerate(coaching.tips):
        assert _tip_contains_number(tip, numbers), (
            f"Fixture {report.current_rank}: tip[{i}] contains no input number.\n"
            f"  tip: {tip!r}\n"
            f"  input numbers: {numbers}"
        )

    # top_weakness must reference a stat that is below median
    assert _weakness_references_below_median(coaching.top_weakness, report), (
        f"Fixture {report.current_rank}: top_weakness does not reference a below-median stat.\n"
        f"  top_weakness: {coaching.top_weakness!r}\n"
        f"  below-median stats: {get_below_median_stats(report)}"
    )
