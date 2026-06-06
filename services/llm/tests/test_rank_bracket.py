"""Gate tests for rank bracket prompt tuning and cost logging."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import json
import pytest
from unittest.mock import MagicMock, patch
from contracts.schemas import RiotReport, MatchStat
from services.llm.coach import _get_rank_bracket, build_prompt, _log_cost


def _report(rank: str) -> RiotReport:
    return RiotReport(
        puuid="p", game_name="Player", tag_line="NA1",
        current_rank=rank, rank_delta=0,
        matches=[MatchStat("m1", "Jett", "Vandal", 10, 8, 2, 22.0, 130.0, True)],
        avg_headshot_pct=22.0, avg_adr=130.0,
        top_agent="Jett", top_weapon="Vandal", win_rate=0.5,
    )


# ------------------------------------------------------------------
# Rank bracket mapping — 10 parametrized cases
# ------------------------------------------------------------------

@pytest.mark.parametrize("rank,expected_label", [
    ("Iron 1",        "Iron/Bronze"),
    ("Iron 3",        "Iron/Bronze"),
    ("Bronze 2",      "Iron/Bronze"),
    ("Silver 1",      "Silver/Gold"),
    ("Gold 3",        "Silver/Gold"),
    ("Platinum 1",    "Platinum/Diamond"),
    ("Diamond 3",     "Platinum/Diamond"),
    ("Ascendant 2",   "Platinum/Diamond"),
    ("Immortal 1",    "Immortal/Radiant"),
    ("Radiant",       "Immortal/Radiant"),
])
def test_rank_bracket_label(rank, expected_label):
    label, _ = _get_rank_bracket(rank)
    assert label == expected_label


def test_rank_bracket_unranked_defaults_to_silver_gold():
    label, _ = _get_rank_bracket("Unranked")
    assert label == "Silver/Gold"


def test_rank_bracket_none_defaults_to_silver_gold():
    label, _ = _get_rank_bracket(None)
    assert label == "Silver/Gold"


# ------------------------------------------------------------------
# Prompt content — bracket injected, and Iron != Diamond
# ------------------------------------------------------------------

def test_build_prompt_contains_bracket_info():
    prompt = build_prompt(_report("Gold 2"))
    assert "Silver/Gold" in prompt
    assert "coaching focus" in prompt.lower()


def test_iron_and_diamond_prompts_differ():
    iron_prompt    = build_prompt(_report("Iron 1"))
    diamond_prompt = build_prompt(_report("Diamond 3"))
    # The bracket line is different — prompts cannot be identical
    assert iron_prompt != diamond_prompt
    assert "Iron/Bronze" in iron_prompt
    assert "Platinum/Diamond" in diamond_prompt


def test_adr_estimated_label_in_prompt():
    report = _report("Gold 1")
    report.adr_is_estimated = True
    report.avg_adr = 145.0
    prompt = build_prompt(report)
    assert "145 (estimated)" in prompt


def test_adr_not_estimated_has_no_label():
    report = _report("Gold 1")
    report.adr_is_estimated = False
    report.avg_adr = 145.0
    prompt = build_prompt(report)
    assert "(estimated)" not in prompt


# ------------------------------------------------------------------
# Cost logging — 2 gate tests
# ------------------------------------------------------------------

def test_log_cost_writes_valid_jsonl(tmp_path, monkeypatch):
    log_file = tmp_path / "costs.jsonl"
    monkeypatch.setenv("LLM_COST_LOG", str(log_file))
    _log_cost("claude-haiku-4-5", input_tokens=500, output_tokens=200)
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["model"] == "claude-haiku-4-5"
    assert entry["input_tokens"] == 500
    assert entry["output_tokens"] == 200
    assert entry["cost_usd"] > 0
    assert "ts" in entry


def test_log_cost_appends_multiple_entries(tmp_path, monkeypatch):
    log_file = tmp_path / "costs.jsonl"
    monkeypatch.setenv("LLM_COST_LOG", str(log_file))
    _log_cost("claude-haiku-4-5", 100, 50)
    _log_cost("claude-haiku-4-5", 200, 80)
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 2
    totals = sum(json.loads(l)["input_tokens"] for l in lines)
    assert totals == 300
