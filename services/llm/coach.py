"""LLM coaching service — generates personalised Valorant aim coaching reports."""

from __future__ import annotations

import json
import os
import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import anthropic
from dotenv import load_dotenv

from contracts.schemas import RiotReport, CVReport, CoachingReport
from services.logging import configure_logging, get_logger

load_dotenv()
configure_logging()
logger = get_logger("services.llm.coach")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL             = os.getenv("LLM_MODEL", "claude-haiku-4-5")

# Cost per million tokens by model (input, output)
_MODEL_COST_PER_MTOK: dict[str, dict[str, float]] = {
    "claude-haiku-4-5":          {"input": 0.80, "output": 4.00},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
    "claude-sonnet-4-5":         {"input": 3.00, "output": 15.00},
    "claude-sonnet-4-6":         {"input": 3.00, "output": 15.00},
    "claude-opus-4-5":           {"input": 15.00, "output": 75.00},
    "claude-opus-4-8":           {"input": 15.00, "output": 75.00},
}

# Rank bracket → (label, coaching focus)
_RANK_BRACKETS: dict[str, tuple[str, str]] = {
    "Iron":      ("Iron/Bronze",      "crosshair placement, economy basics, agent utility"),
    "Bronze":    ("Iron/Bronze",      "crosshair placement, economy basics, agent utility"),
    "Silver":    ("Silver/Gold",      "map control, trade discipline, peeking angles"),
    "Gold":      ("Silver/Gold",      "map control, trade discipline, peeking angles"),
    "Platinum":  ("Platinum/Diamond", "anti-strafe timing, spray transfers, rotations, info plays"),
    "Diamond":   ("Platinum/Diamond", "anti-strafe timing, spray transfers, rotations, info plays"),
    "Ascendant": ("Platinum/Diamond", "anti-strafe timing, spray transfers, rotations, info plays"),
    "Immortal":  ("Immortal/Radiant", "mental game, opponent reads, meta adaptation"),
    "Radiant":   ("Immortal/Radiant", "mental game, opponent reads, meta adaptation"),
}
_DEFAULT_BRACKET = ("Silver/Gold", "map control, trade discipline, peeking angles")

SYSTEM_PROMPT = (
    "You are an expert Valorant aim coach. Analyse the player statistics provided "
    "and identify the most impactful aiming mistakes. Be direct, specific, and actionable. "
    "Reference exact numbers from the data — never be vague. "
    "The player's skill bracket and coaching focus will be provided — tailor your advice "
    "to that bracket: fundamentals for Iron/Bronze, mechanical refinement for Platinum/Diamond, "
    "strategic depth for Immortal/Radiant. "
    "Respond ONLY with valid JSON matching the schema below. No prose outside the JSON.\n\n"
    "Schema:\n"
    '{\n'
    '  "summary": "string — 2-3 sentences. Mention rank, HS%, win rate.",\n'
    '  "top_weakness": "string — the single biggest issue. Reference a specific stat.",\n'
    '  "tips": ["string", ...],  // 3-5 items. Each tip references a number from the data.\n'
    '  "encouragement": "string — one genuine closing line."\n'
    '}'
)


def _get_rank_bracket(rank: str | None) -> tuple[str, str]:
    if not rank or rank == "Unranked":
        return _DEFAULT_BRACKET
    for prefix, data in _RANK_BRACKETS.items():
        if rank.startswith(prefix):
            return data
    return _DEFAULT_BRACKET


def _log_cost(model: str, input_tokens: int, output_tokens: int) -> None:
    try:
        in_tok  = int(input_tokens)
        out_tok = int(output_tokens)
    except (TypeError, ValueError):
        return  # gracefully skip when called with mock objects in tests
    rates = _MODEL_COST_PER_MTOK.get(model, {"input": 0.0, "output": 0.0})
    cost_usd = (in_tok * rates["input"] + out_tok * rates["output"]) / 1_000_000
    entry = {
        "ts": time.time(),
        "model": model,
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "cost_usd": round(cost_usd, 6),
    }
    log_path = os.getenv("LLM_COST_LOG", "llm_costs.jsonl")
    try:
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError as exc:
        logger.warning("Could not write cost log to %s: %s", log_path, exc)


def build_prompt(riot: RiotReport, cv: CVReport | None = None) -> str:
    n = len(riot.matches)
    bracket_label, bracket_focus = _get_rank_bracket(riot.current_rank)
    adr_note = " (estimated)" if riot.adr_is_estimated else ""

    lines = [
        f"Player: {riot.game_name}#{riot.tag_line}",
        f"Rank: {riot.current_rank} (rank change over last matches: {riot.rank_delta:+d})",
        f"Skill bracket: {bracket_label} — coaching focus for this tier: {bracket_focus}",
        f"Last {n} matches:",
        f"  Win rate:          {riot.win_rate * 100:.0f}%",
        f"  Avg headshot %:    {riot.avg_headshot_pct:.1f}%",
        f"  Avg ADR:           {riot.avg_adr:.0f}{adr_note}",
        f"  Most-played agent: {riot.top_agent}",
        f"  Most-used weapon:  {riot.top_weapon}",
    ]

    # Recent match breakdown (last 5)
    if riot.matches:
        lines.append("\nRecent matches (newest first):")
        for m in riot.matches[:5]:
            result = "W" if m.won else "L"
            lines.append(
                f"  [{result}] {m.agent} — {m.kills}/{m.deaths}/{m.assists} "
                f"HS%:{m.headshot_pct:.0f}% ADR:{m.adr:.0f} weapon:{m.weapon}"
            )

    # CV clip analysis (Phase 2)
    if cv is not None:
        lines.append(f"\nClip analysis ({cv.total_engagements} engagements, {cv.duration_s:.0f}s):")
        lines.append(f"  Mistakes per minute: {cv.mistakes_per_minute:.1f}")
        lines.append(f"  Most impactful mistake: {cv.most_impactful or 'none detected'}")
        if cv.ranked_mistakes:
            lines.append("  Top mistakes by impact:")
            for r in cv.ranked_mistakes[:3]:
                lines.append(
                    f"    {r['rank']}. {r['label']} — x{r['count']} "
                    f"(avg severity {r['avg_severity']:.2f}, {r['share_of_total']})"
                )

    lines.append("\nProvide coaching based on this data.")
    return "\n".join(lines)


async def generate_coaching_report(
    riot: RiotReport,
    cv: CVReport | None = None,
) -> CoachingReport:
    """Call Claude and parse the JSON response into a CoachingReport."""
    if not ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY is not set")
        raise ValueError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")

    logger.info("Generating coaching report for %s#%s using model=%s", riot.game_name, riot.tag_line, MODEL)
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = build_prompt(riot, cv)
    logger.debug("Built coaching prompt length=%d", len(prompt))

    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    _log_cost(MODEL, message.usage.input_tokens, message.usage.output_tokens)

    # Strip markdown code fences if Claude wraps the JSON
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Claude response not valid JSON, retrying once")
        retry_msg = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user",  "content": prompt},
                {"role": "assistant", "content": raw},
                {"role": "user",  "content": "Your response was not valid JSON. Reply with valid JSON only, no other text."},
            ],
        )
        raw = retry_msg.content[0].text.strip()
        _log_cost(MODEL, retry_msg.usage.input_tokens, retry_msg.usage.output_tokens)
        parsed = json.loads(raw)

    return CoachingReport(
        summary=parsed["summary"],
        top_weakness=parsed["top_weakness"],
        tips=parsed["tips"],
        encouragement=parsed["encouragement"],
        raw_response=raw,
    )
