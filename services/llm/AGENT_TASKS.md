# LLM Service — Agent Implementation Task

## Context
Takes a `RiotReport` (+ optional `CVReport`) and returns a `CoachingReport`
via the Anthropic API. This is the "AI coaching" feature — the core value proposition.

## What exists
- `coach.py` — stubbed with prompt template skeleton
- `requirements.txt`

## What to build

### 1. `coach.py` — implement `build_prompt` and `generate_coaching_report`

**`build_prompt(riot, cv) → str`**

Build a structured prompt. Be specific — include actual numbers.

Example structure:
```
Player: {riot.game_name}#{riot.tag_line}
Rank: {riot.current_rank} (delta: {riot.rank_delta:+d} LP last match)
Last {len(riot.matches)} matches:
  Win rate: {riot.win_rate*100:.0f}%
  Avg headshot %: {riot.avg_headshot_pct:.1f}%
  Avg ADR: {riot.avg_adr:.0f}
  Top agent: {riot.top_agent}
  Top weapon: {riot.top_weapon}

[If cv is not None:]
Clip analysis ({cv.total_engagements} engagements, {cv.duration_s:.0f}s clip):
  Most impactful mistake: {cv.most_impactful}
  Mistakes per minute: {cv.mistakes_per_minute}
  [List top 3 mistakes with counts and severities]

Respond in JSON:
{
  "summary": "2-3 sentences. Be specific about their numbers.",
  "top_weakness": "Single biggest issue. Reference a specific stat.",
  "tips": ["3-5 actionable tips. Each references a specific number or pattern."],
  "encouragement": "One genuine closing line."
}
```

**`generate_coaching_report(riot, cv) → CoachingReport`**

```python
import anthropic
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

message = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": build_prompt(riot, cv)}]
)

raw = message.content[0].text
parsed = json.loads(raw)
return CoachingReport(
    summary=parsed["summary"],
    top_weakness=parsed["top_weakness"],
    tips=parsed["tips"],
    encouragement=parsed["encouragement"],
    raw_response=raw,
)
```

Add error handling: if JSON parse fails, retry once with "respond only in valid JSON".

### 2. Add `tests/test_coach.py`

- Mock the Anthropic client (don't make real API calls in tests)
- Test `build_prompt` outputs correct structure with fixture RiotReport
- Test `generate_coaching_report` parses valid JSON response correctly
- Test malformed JSON response triggers retry

### 3. Add `eval/eval_coaching_quality.py`

Periodic eval (not gate test — makes real API calls):
- Send 5 fixture RiotReports with varying stats
- Check response is not generic: assert tips contain numbers from the input
- Check response length: summary 2-3 sentences, tips 3-5 items
- Log pass/fail + cost per call

## Done criteria
- `generate_coaching_report(riot_report)` returns a populated `CoachingReport`
- Prompt includes specific numbers, not vague descriptions
- `pytest services/llm/tests/` passes (mocked)
- Eval script runs and logs cost per call
