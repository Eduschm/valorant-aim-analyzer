"""
Eval: Iron vs Diamond inputs must produce measurably different coaching.

These are deterministic gate tests — they verify prompt-construction logic,
not live LLM output, so they run on every commit with no API cost.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from contracts.schemas import RiotReport, MatchStat
from services.llm.coach import _get_bracket_context, _build_system_prompt, build_prompt

# Identical stats — only rank differs
_BASE_STATS = dict(
    puuid="eval-puuid",
    game_name="EvalPlayer",
    tag_line="NA1",
    rank_delta=0,
    matches=[
        MatchStat("m1", "Jett", "Vandal", 15, 15, 3, 22.0, 140.0, True),
        MatchStat("m2", "Jett", "Vandal", 12, 14, 5, 18.0, 110.0, False),
    ],
    avg_headshot_pct=20.0,
    avg_adr=125.0,
    top_agent="Jett",
    top_weapon="Vandal",
    win_rate=0.5,
)

IRON_REPORT    = RiotReport(**_BASE_STATS, current_rank="Iron 2")
BRONZE_REPORT  = RiotReport(**_BASE_STATS, current_rank="Bronze 3")
SILVER_REPORT  = RiotReport(**_BASE_STATS, current_rank="Silver 1")
GOLD_REPORT    = RiotReport(**_BASE_STATS, current_rank="Gold 2")
PLATINUM_REPORT = RiotReport(**_BASE_STATS, current_rank="Platinum 1")
DIAMOND_REPORT = RiotReport(**_BASE_STATS, current_rank="Diamond 3")
IMMORTAL_REPORT = RiotReport(**_BASE_STATS, current_rank="Immortal 2")
RADIANT_REPORT  = RiotReport(**_BASE_STATS, current_rank="Radiant")


# ------------------------------------------------------------------ bracket context


def test_iron_context_mentions_fundamentals():
    ctx = _get_bracket_context("Iron 2")
    assert any(kw in ctx.lower() for kw in ["crosshair", "placement", "fundamental", "economy"])


def test_diamond_context_mentions_advanced_mechanics():
    ctx = _get_bracket_context("Diamond 3")
    assert any(kw in ctx.lower() for kw in ["anti-strafe", "spray", "rotation", "information"])


def test_immortal_context_mentions_mental_game():
    ctx = _get_bracket_context("Immortal 1")
    assert any(kw in ctx.lower() for kw in ["mental", "opponent", "meta"])


def test_iron_and_bronze_share_bracket():
    assert _get_bracket_context("Iron 1") == _get_bracket_context("Bronze 1")


def test_silver_and_gold_share_bracket():
    assert _get_bracket_context("Silver 2") == _get_bracket_context("Gold 3")


def test_platinum_and_diamond_share_bracket():
    assert _get_bracket_context("Platinum 2") == _get_bracket_context("Diamond 1")


def test_immortal_and_radiant_share_bracket():
    assert _get_bracket_context("Immortal 3") == _get_bracket_context("Radiant")


# ------------------------------------------------------------------ system prompt differences


def test_system_prompt_differs_across_all_four_brackets():
    prompts = [
        _build_system_prompt("Iron 1"),
        _build_system_prompt("Silver 1"),
        _build_system_prompt("Platinum 1"),
        _build_system_prompt("Immortal 1"),
    ]
    assert len(set(prompts)) == 4, "Each bracket must produce a unique system prompt"


def test_iron_system_prompt_contains_iron_label():
    assert "Iron/Bronze" in _build_system_prompt("Iron 2")


def test_diamond_system_prompt_contains_diamond_label():
    assert "Platinum/Diamond" in _build_system_prompt("Diamond 3")


# ------------------------------------------------------------------ no tip copy-paste (prompt-level)


def test_prompts_with_same_stats_differ_only_by_bracket():
    """Same stats → user prompt identical; system prompt must differ for Iron vs Diamond."""
    iron_user    = build_prompt(IRON_REPORT)
    diamond_user = build_prompt(DIAMOND_REPORT)
    # User prompt content is the same (same stats, only rank string differs)
    iron_sys    = _build_system_prompt(IRON_REPORT.current_rank)
    diamond_sys = _build_system_prompt(DIAMOND_REPORT.current_rank)
    assert iron_sys != diamond_sys
    # The rank line in the user prompt will differ
    assert "Iron 2"    in iron_user
    assert "Diamond 3" in diamond_user
