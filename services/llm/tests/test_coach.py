"""Gate tests for LLM coach — mocked, no real API calls."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import json
import pytest
from unittest.mock import MagicMock, patch
from contracts.schemas import RiotReport, MatchStat, CoachingReport
from services.llm.coach import (
    build_prompt,
    generate_coaching_report,
    _get_bracket_context,
    _build_system_prompt,
    _log_cost,
    RANK_BRACKETS,
)


RIOT_REPORT = RiotReport(
    puuid="test-puuid",
    game_name="TestPlayer",
    tag_line="NA1",
    current_rank="Gold 2",
    rank_delta=15,
    matches=[
        MatchStat("m1", "Jett", "Vandal", 18, 12, 3, 25.0, 160.0, True),
        MatchStat("m2", "Jett", "Vandal", 10, 15, 5, 18.0, 120.0, False),
    ],
    avg_headshot_pct=21.5,
    avg_adr=140.0,
    top_agent="Jett",
    top_weapon="Vandal",
    win_rate=0.5,
)

VALID_RESPONSE = json.dumps({
    "summary": "TestPlayer is Gold 2 with a 50% win rate and 21.5% headshot percentage.",
    "top_weakness": "Headshot rate of 21.5% is below the Gold average of ~28%.",
    "tips": [
        "Your 21.5% HS rate suggests crosshair placement issues — keep it at head height.",
        "ADR of 140 is decent but your 10/15 loss shows inconsistency under pressure.",
        "On Vandal, burst at range — don't spray past 3 bullets.",
    ],
    "encouragement": "The fundamentals are there — sharpen crosshair placement and the rank will follow.",
})


def _make_mock_message(text: str) -> MagicMock:
    content = MagicMock()
    content.text = text
    usage = MagicMock()
    usage.input_tokens  = 100
    usage.output_tokens = 200
    msg = MagicMock()
    msg.content = [content]
    msg.usage   = usage
    return msg


# ------------------------------------------------------------------ build_prompt


def test_build_prompt_contains_numbers():
    prompt = build_prompt(RIOT_REPORT)
    assert "21.5" in prompt
    assert "140"  in prompt
    assert "50%"  in prompt
    assert "Gold 2" in prompt
    assert "Jett"   in prompt
    assert "Vandal" in prompt


def test_build_prompt_has_match_history():
    prompt = build_prompt(RIOT_REPORT)
    assert "18/12/3" in prompt or "18" in prompt


def test_build_prompt_no_cv():
    prompt = build_prompt(RIOT_REPORT, cv=None)
    assert "Clip analysis" not in prompt


# ------------------------------------------------------------------ rank brackets


def test_get_bracket_context_iron():
    ctx = _get_bracket_context("Iron 2")
    assert "Iron/Bronze" in ctx
    assert "crosshair placement" in ctx.lower()


def test_get_bracket_context_diamond():
    ctx = _get_bracket_context("Diamond 3")
    assert "Platinum/Diamond" in ctx
    assert "anti-strafe" in ctx.lower()


def test_get_bracket_context_immortal():
    ctx = _get_bracket_context("Immortal 1")
    assert "Immortal/Radiant" in ctx
    assert "mental game" in ctx.lower()


def test_get_bracket_context_unknown_rank():
    ctx = _get_bracket_context("Unranked")
    assert "skill level" in ctx.lower()


def test_build_system_prompt_differs_by_bracket():
    iron_prompt    = _build_system_prompt("Iron 1")
    diamond_prompt = _build_system_prompt("Diamond 2")
    immortal_prompt = _build_system_prompt("Immortal 3")
    assert iron_prompt    != diamond_prompt
    assert diamond_prompt != immortal_prompt
    assert iron_prompt    != immortal_prompt


def test_all_defined_brackets_produce_unique_contexts():
    unique_contexts = {_get_bracket_context(f"{rank.capitalize()} 1") for rank in RANK_BRACKETS}
    # iron+bronze collapse to one, silver+gold to one, platinum+diamond to one, immortal+radiant to one = 4
    assert len(unique_contexts) == 4


# ------------------------------------------------------------------ cost logging


def test_log_cost_writes_jsonl_entry(tmp_path):
    log_path = tmp_path / "costs.jsonl"
    with patch("services.llm.coach.COST_LOG_FILE", str(log_path)):
        _log_cost("claude-haiku-4-5", 1000, 500)

    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["model"]         == "claude-haiku-4-5"
    assert entry["input_tokens"]  == 1000
    assert entry["output_tokens"] == 500
    assert entry["cost_usd"]      > 0
    assert "timestamp" in entry


def test_log_cost_appends_multiple_entries(tmp_path):
    log_path = tmp_path / "costs.jsonl"
    with patch("services.llm.coach.COST_LOG_FILE", str(log_path)):
        _log_cost("claude-haiku-4-5", 100, 50)
        _log_cost("claude-haiku-4-5", 200, 100)

    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 2


def test_log_cost_haiku_pricing():
    """Verify haiku input cost is cheaper than sonnet."""
    import services.llm.coach as coach
    haiku_rate  = coach._COST_RATES["claude-haiku-4-5"]["input"]
    sonnet_rate = coach._COST_RATES["claude-sonnet-4-6"]["input"]
    assert haiku_rate < sonnet_rate


# ------------------------------------------------------------------ generate_coaching_report


@pytest.mark.asyncio
async def test_generate_coaching_report_parses_valid_json():
    mock_message = _make_mock_message(VALID_RESPONSE)

    with patch("services.llm.coach.anthropic.Anthropic") as MockClient, \
         patch("services.llm.coach.ANTHROPIC_API_KEY", "test-key"), \
         patch("services.llm.coach._log_cost"):
        MockClient.return_value.messages.create.return_value = mock_message
        report = await generate_coaching_report(RIOT_REPORT)

    assert isinstance(report, CoachingReport)
    assert "21.5%" in report.top_weakness
    assert len(report.tips) == 3
    assert report.summary != ""
    assert report.encouragement != ""


@pytest.mark.asyncio
async def test_generate_coaching_report_retries_on_bad_json():
    bad_msg  = _make_mock_message("This is not JSON")
    good_msg = _make_mock_message(VALID_RESPONSE)

    with patch("services.llm.coach.anthropic.Anthropic") as MockClient, \
         patch("services.llm.coach.ANTHROPIC_API_KEY", "test-key"), \
         patch("services.llm.coach._log_cost"):
        MockClient.return_value.messages.create.side_effect = [bad_msg, good_msg]
        report = await generate_coaching_report(RIOT_REPORT)

    assert MockClient.return_value.messages.create.call_count == 2
    assert isinstance(report, CoachingReport)


@pytest.mark.asyncio
async def test_generate_coaching_report_strips_markdown_fence():
    fenced  = f"```json\n{VALID_RESPONSE}\n```"
    mock_message = _make_mock_message(fenced)

    with patch("services.llm.coach.anthropic.Anthropic") as MockClient, \
         patch("services.llm.coach.ANTHROPIC_API_KEY", "test-key"), \
         patch("services.llm.coach._log_cost"):
        MockClient.return_value.messages.create.return_value = mock_message
        report = await generate_coaching_report(RIOT_REPORT)

    assert isinstance(report, CoachingReport)


@pytest.mark.asyncio
async def test_generate_coaching_report_uses_bracket_system_prompt():
    """Iron and Diamond reports should be sent with different system prompts."""
    iron_report    = RiotReport(**{**RIOT_REPORT.__dict__, "current_rank": "Iron 2"})
    diamond_report = RiotReport(**{**RIOT_REPORT.__dict__, "current_rank": "Diamond 3"})

    captured_systems: list[str] = []

    def _create(*args, **kwargs):
        captured_systems.append(kwargs.get("system", ""))
        return _make_mock_message(VALID_RESPONSE)

    with patch("services.llm.coach.anthropic.Anthropic") as MockClient, \
         patch("services.llm.coach.ANTHROPIC_API_KEY", "test-key"), \
         patch("services.llm.coach._log_cost"):
        MockClient.return_value.messages.create.side_effect = _create
        await generate_coaching_report(iron_report)
        await generate_coaching_report(diamond_report)

    assert captured_systems[0] != captured_systems[1]
    assert "Iron/Bronze"      in captured_systems[0]
    assert "Platinum/Diamond" in captured_systems[1]


@pytest.mark.asyncio
async def test_generate_coaching_report_logs_cost():
    """Each successful call must emit a cost log entry."""
    mock_message = _make_mock_message(VALID_RESPONSE)
    logged: list = []

    def capture_log(model, inp, out):
        logged.append({"model": model, "input": inp, "output": out})

    with patch("services.llm.coach.anthropic.Anthropic") as MockClient, \
         patch("services.llm.coach.ANTHROPIC_API_KEY", "test-key"), \
         patch("services.llm.coach._log_cost", side_effect=capture_log):
        MockClient.return_value.messages.create.return_value = mock_message
        await generate_coaching_report(RIOT_REPORT)

    assert len(logged) == 1
    assert logged[0]["model"] == "claude-haiku-4-5"
