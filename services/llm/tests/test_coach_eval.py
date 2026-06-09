"""
Periodic eval for the LLM coaching report.

These tests call generate_coaching_report() with a real Anthropic API key.
They are slow and cost money. Run with:

    pytest -m eval services/llm/tests/test_coach_eval.py -v

Requires: ANTHROPIC_API_KEY set in environment.
Pass threshold: 3/3 runs pass (deterministic for well-formed prompts).
"""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from contracts.schemas import RiotReport, MatchStat, CoachingReport

EVAL_REPORT = RiotReport(
    puuid="eval-puuid",
    game_name="EvalPlayer",
    tag_line="NA1",
    current_rank="Gold 2",
    rank_delta=5,
    matches=[
        MatchStat("m1", "Jett", "Vandal", 18, 12, 3, 25.0, 160.0, True),
        MatchStat("m2", "Jett", "Vandal", 10, 15, 5, 18.0, 120.0, False),
        MatchStat("m3", "Sage", "Phantom", 14, 13, 8, 30.0, 140.0, True),
    ],
    avg_headshot_pct=24.3,
    avg_adr=140.0,
    top_agent="Jett",
    top_weapon="Vandal",
    win_rate=0.67,
)


@pytest.mark.eval
@pytest.mark.asyncio
async def test_eval_coaching_report_valid_json():
    """Real API call: response must be valid CoachingReport with all fields."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set — skipping live eval")

    from services.llm.coach import generate_coaching_report

    report = await generate_coaching_report(EVAL_REPORT)

    assert isinstance(report, CoachingReport), "Should return a CoachingReport dataclass"
    assert report.summary, "summary must not be empty"
    assert report.top_weakness, "top_weakness must not be empty"
    assert 3 <= len(report.tips) <= 5, f"tips count {len(report.tips)} outside [3,5]"
    assert report.encouragement, "encouragement must not be empty"
    assert all(t for t in report.tips), "no tip should be an empty string"


@pytest.mark.eval
@pytest.mark.asyncio
async def test_eval_coaching_report_references_stats():
    """Real API call: coaching must reference at least one concrete stat from the input."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set — skipping live eval")

    from services.llm.coach import generate_coaching_report

    report = await generate_coaching_report(EVAL_REPORT)

    full_text = " ".join([report.summary, report.top_weakness] + report.tips + [report.encouragement])
    # At least one stat from the input should appear somewhere in the coaching text
    stat_references = ["24", "140", "Gold", "Jett", "Vandal", "67%", "0.67"]
    assert any(s in full_text for s in stat_references), (
        f"Coaching text has no reference to input stats. Got:\n{full_text}"
    )
