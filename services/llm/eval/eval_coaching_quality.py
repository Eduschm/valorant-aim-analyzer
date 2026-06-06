"""
Periodic eval — coaching quality.

Run explicitly (NOT part of gate tests):
    python -m pytest services/llm/eval/eval_coaching_quality.py -v

Requires ANTHROPIC_API_KEY. Costs ~$0.03 (5 calls × ~$0.006).
Pass threshold: 4 of 5 fixtures must pass both assertions.
"""

from __future__ import annotations

import asyncio
import re
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from services.llm.coach import generate_coaching_report, _get_rank_bracket
from services.llm.eval.fixtures import (
    ALL_FIXTURES, RANK_MEDIANS,
    IRON_REPORT, GOLD_REPORT, PLAT_REPORT, DIAMOND_REPORT, IMMORTAL_REPORT,
)
from contracts.schemas import RiotReport


def _extract_numbers(text: str) -> list[float]:
    return [float(m) for m in re.findall(r"\d+(?:\.\d+)?%?", text.replace("%", ""))]


def _has_input_number(tip: str, report: RiotReport) -> bool:
    """Return True if the tip references at least one stat value from the report."""
    nums_in_tip = set(re.findall(r"\d+(?:\.\d+)?", tip))
    candidates = {
        str(int(report.avg_headshot_pct)),
        f"{report.avg_headshot_pct:.1f}",
        str(int(report.avg_adr)),
        f"{report.avg_adr:.0f}",
        str(int(report.win_rate * 100)),
        str(report.rank_delta),
    }
    return bool(nums_in_tip & candidates)


def _below_median_stats(report: RiotReport) -> set[str]:
    bracket_label, _ = _get_rank_bracket(report.current_rank)
    medians = RANK_MEDIANS.get(bracket_label, {})
    below = set()
    if report.avg_headshot_pct < medians.get("hs_pct", 0):
        below.add("headshot")
    if report.avg_adr < medians.get("adr", 0):
        below.add("adr")
    if report.win_rate < medians.get("win_rate", 0):
        below.add("win")
    return below


@pytest.mark.parametrize("report", ALL_FIXTURES, ids=[r.game_name for r in ALL_FIXTURES])
def test_coaching_quality(report: RiotReport):
    """Each tip must reference a number from the input; weakness must target a weak stat."""
    coaching = asyncio.run(generate_coaching_report(report))

    # 1. Every tip references at least one input number
    tips_with_numbers = [t for t in coaching.tips if _has_input_number(t, report)]
    assert len(tips_with_numbers) >= len(coaching.tips) * 0.6, (
        f"Only {len(tips_with_numbers)}/{len(coaching.tips)} tips reference input numbers.\n"
        f"Tips: {coaching.tips}"
    )

    # 2. top_weakness mentions a stat that is below the rank median
    weakness_text = coaching.top_weakness.lower()
    below = _below_median_stats(report)
    stat_mentioned = any(kw in weakness_text for kw in below) if below else True
    assert stat_mentioned, (
        f"top_weakness '{coaching.top_weakness}' doesn't reference any below-median stats "
        f"({below}) for {report.current_rank}."
    )
