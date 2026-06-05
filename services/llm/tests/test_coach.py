"""Gate tests for LLM coach — mocked, no real API calls."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import json
import pytest
from unittest.mock import MagicMock, patch
from contracts.schemas import RiotReport, MatchStat, CoachingReport
from services.llm.coach import build_prompt, generate_coaching_report


RIOT_REPORT = RiotReport(
    puuid="test-puuid",
    game_name="TestPlayer",
    tag_line="NA1",
    current_rank="Gold 2",
    rank_delta=15,
    matches=[
        MatchStat("m1","Jett","Vandal",18,12,3,25.0,160.0,True),
        MatchStat("m2","Jett","Vandal",10,15,5,18.0,120.0,False),
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


def test_build_prompt_contains_numbers():
    prompt = build_prompt(RIOT_REPORT)
    assert "21.5" in prompt          # avg HS%
    assert "140" in prompt           # avg ADR
    assert "50%" in prompt           # win rate
    assert "Gold 2" in prompt        # rank
    assert "Jett" in prompt          # top agent
    assert "Vandal" in prompt        # top weapon


def test_build_prompt_has_match_history():
    prompt = build_prompt(RIOT_REPORT)
    assert "18/12/3" in prompt or "18" in prompt


def test_build_prompt_no_cv():
    prompt = build_prompt(RIOT_REPORT, cv=None)
    assert "Clip analysis" not in prompt


@pytest.mark.asyncio
async def test_generate_coaching_report_parses_valid_json(tmp_path):
    mock_content = MagicMock()
    mock_content.text = VALID_RESPONSE
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_message.usage   = MagicMock(input_tokens=100, output_tokens=200)

    with patch("services.llm.coach.anthropic.Anthropic") as MockClient, \
         patch("services.llm.coach.ANTHROPIC_API_KEY", "test-key"), \
         patch("services.llm.coach.COST_LOG_PATH", str(tmp_path / "costs.jsonl")):
        instance = MockClient.return_value
        instance.messages.create.return_value = mock_message
        report = await generate_coaching_report(RIOT_REPORT)

    assert isinstance(report, CoachingReport)
    assert "21.5%" in report.top_weakness
    assert len(report.tips) == 3
    assert report.summary != ""
    assert report.encouragement != ""


@pytest.mark.asyncio
async def test_generate_coaching_report_retries_on_bad_json(tmp_path):
    bad_response  = MagicMock(); bad_response.text  = "This is not JSON"
    good_response = MagicMock(); good_response.text = VALID_RESPONSE
    mock_message_bad  = MagicMock(); mock_message_bad.content  = [bad_response]
    mock_message_good = MagicMock(); mock_message_good.content = [good_response]
    mock_message_bad.usage  = MagicMock(input_tokens=80, output_tokens=50)
    mock_message_good.usage = MagicMock(input_tokens=90, output_tokens=200)

    with patch("services.llm.coach.anthropic.Anthropic") as MockClient, \
         patch("services.llm.coach.ANTHROPIC_API_KEY", "test-key"), \
         patch("services.llm.coach.COST_LOG_PATH", str(tmp_path / "costs.jsonl")):
        instance = MockClient.return_value
        instance.messages.create.side_effect = [mock_message_bad, mock_message_good]
        report = await generate_coaching_report(RIOT_REPORT)

    assert instance.messages.create.call_count == 2
    assert isinstance(report, CoachingReport)


@pytest.mark.asyncio
async def test_generate_coaching_report_strips_markdown_fence(tmp_path):
    fenced = f"```json\n{VALID_RESPONSE}\n```"
    mock_content = MagicMock(); mock_content.text = fenced
    mock_message = MagicMock(); mock_message.content = [mock_content]
    mock_message.usage = MagicMock(input_tokens=100, output_tokens=200)

    with patch("services.llm.coach.anthropic.Anthropic") as MockClient, \
         patch("services.llm.coach.ANTHROPIC_API_KEY", "test-key"), \
         patch("services.llm.coach.COST_LOG_PATH", str(tmp_path / "costs.jsonl")):
        instance = MockClient.return_value
        instance.messages.create.return_value = mock_message
        report = await generate_coaching_report(RIOT_REPORT)

    assert isinstance(report, CoachingReport)
