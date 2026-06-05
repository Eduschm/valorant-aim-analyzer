"""Gate tests for rank-bracket prompt tuning."""

from __future__ import annotations

import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from unittest.mock import MagicMock, patch

from contracts.schemas import RiotReport, MatchStat
from services.llm.coach import build_prompt, _get_rank_bracket, generate_coaching_report


def _make_report(rank: str) -> RiotReport:
    return RiotReport(
        puuid="test-puuid",
        game_name="Player",
        tag_line="NA1",
        current_rank=rank,
        rank_delta=0,
        matches=[MatchStat("m1", "Jett", "Vandal", 15, 10, 3, 22.0, 130.0, True)],
        avg_headshot_pct=22.0,
        avg_adr=130.0,
        top_agent="Jett",
        top_weapon="Vandal",
        win_rate=0.5,
    )


VALID_RESPONSE = json.dumps({
    "summary": "Player is Gold 2.",
    "top_weakness": "HS% of 22% is below the Gold average.",
    "tips": ["Keep crosshair at head height at 22%.", "ADR of 130 needs improvement."],
    "encouragement": "Keep at it.",
})


# ------------------------------------------------------------------ #
# _get_rank_bracket                                                    #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("rank,expected_label", [
    ("Iron 1",       "Iron/Bronze"),
    ("Iron 3",       "Iron/Bronze"),
    ("Bronze 2",     "Iron/Bronze"),
    ("Silver 1",     "Silver/Gold"),
    ("Gold 3",       "Silver/Gold"),
    ("Platinum 1",   "Platinum/Diamond"),
    ("Diamond 2",    "Platinum/Diamond"),
    ("Immortal 1",   "Immortal/Radiant"),
    ("Radiant",      "Immortal/Radiant"),
    ("Unranked",     "Unranked/Placement"),
])
def test_get_rank_bracket_label(rank, expected_label):
    bracket = _get_rank_bracket(rank)
    assert bracket["label"] == expected_label


# ------------------------------------------------------------------ #
# build_prompt includes bracket context                                #
# ------------------------------------------------------------------ #

def test_build_prompt_iron_contains_bracket():
    prompt = build_prompt(_make_report("Iron 2"))
    assert "Iron/Bronze" in prompt
    assert "crosshair placement" in prompt.lower()


def test_build_prompt_diamond_contains_bracket():
    prompt = build_prompt(_make_report("Diamond 3"))
    assert "Platinum/Diamond" in prompt
    assert "anti-strafe" in prompt.lower()


def test_build_prompt_immortal_contains_bracket():
    prompt = build_prompt(_make_report("Immortal 2"))
    assert "Immortal/Radiant" in prompt
    assert "mental game" in prompt.lower()


def test_iron_and_diamond_prompts_differ():
    """Iron and Diamond prompts must have different bracket context."""
    iron_prompt    = build_prompt(_make_report("Iron 1"))
    diamond_prompt = build_prompt(_make_report("Diamond 2"))
    # The bracket lines must differ
    assert "Iron/Bronze" in iron_prompt
    assert "Iron/Bronze" not in diamond_prompt
    assert "Platinum/Diamond" in diamond_prompt


# ------------------------------------------------------------------ #
# Cost logging                                                         #
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_cost_logged_after_successful_report(tmp_path):
    """generate_coaching_report writes a cost entry to the log file."""
    log_path = str(tmp_path / "costs.jsonl")
    mock_content = MagicMock(); mock_content.text = VALID_RESPONSE
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_message.usage   = MagicMock(input_tokens=100, output_tokens=200)

    with patch("services.llm.coach.anthropic.Anthropic") as MockClient, \
         patch("services.llm.coach.ANTHROPIC_API_KEY", "test-key"), \
         patch("services.llm.coach.COST_LOG_PATH", log_path):
        instance = MockClient.return_value
        instance.messages.create.return_value = mock_message
        report = await generate_coaching_report(_make_report("Gold 2"))

    import json as _json
    entries = [_json.loads(line) for line in open(log_path)]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["input_tokens"]  == 100
    assert entry["output_tokens"] == 200
    assert entry["cost_usd"]      > 0
    assert entry["model"] in ("claude-haiku-4-5", "")  # model from env/default


@pytest.mark.asyncio
async def test_cost_log_entry_has_all_fields(tmp_path):
    """Each log entry has ts, model, input_tokens, output_tokens, cost_usd."""
    log_path = str(tmp_path / "costs.jsonl")
    mock_content = MagicMock(); mock_content.text = VALID_RESPONSE
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_message.usage   = MagicMock(input_tokens=50, output_tokens=80)

    with patch("services.llm.coach.anthropic.Anthropic") as MockClient, \
         patch("services.llm.coach.ANTHROPIC_API_KEY", "test-key"), \
         patch("services.llm.coach.COST_LOG_PATH", log_path):
        MockClient.return_value.messages.create.return_value = mock_message
        await generate_coaching_report(_make_report("Silver 3"))

    import json as _json
    entry = _json.loads(open(log_path).readline())
    for field in ("ts", "model", "input_tokens", "output_tokens", "cost_usd"):
        assert field in entry, f"Missing field: {field}"
