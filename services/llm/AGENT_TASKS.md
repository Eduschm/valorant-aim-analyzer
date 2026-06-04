# LLM Service

## Status: ✅ DONE

Full implementation exists. No stubs remain.

---

## What's built

| File | Purpose |
|---|---|
| `coach.py` | `build_prompt(riot, cv)` + `generate_coaching_report(riot, cv)` |
| `tests/test_coach.py` | 4 gate tests — mocked Anthropic client, no real API calls |

---

## How to use

```python
from services.llm.coach import generate_coaching_report

coaching = await generate_coaching_report(riot_report, cv_report=None)
# → CoachingReport (contracts/schemas.py)
# Fields: summary, top_weakness, tips[], encouragement, raw_response
```

---

## Running tests

```bash
cd valorant-aim-analyzer
pytest services/llm/tests/ -v
```

---

## Model + cost

| Setting | Value |
|---|---|
| Model | `claude-haiku-4-5` (from `LLM_MODEL` env var) |
| Max tokens | 1024 |
| Cost | ~$0.006 per report at Haiku pricing |
| Retry | Once on JSON parse failure |
| Markdown fence stripping | Yes — handles ```json ... ``` wrapping |

---

## Prompt engineering notes

`build_prompt()` in `coach.py` constructs a structured prompt with exact numbers:
- Rank, rank delta, win rate
- Avg HS%, avg ADR
- Per-match K/D/A breakdown (last 5 matches)
- CV report data when available (Phase 2)

The system prompt instructs Claude to respond in JSON only. The response schema:
```json
{
  "summary": "2-3 sentences with specific stats",
  "top_weakness": "single biggest issue with a stat reference",
  "tips": ["3-5 actionable tips, each with a number"],
  "encouragement": "one closing line"
}
```

---

## Remaining improvements (optional)

- Add `eval/eval_coaching_quality.py` — send 5 fixture reports, assert tips contain numbers from input
- Log cost per call to a metrics file for tracking spend
- Tune prompt for specific rank brackets (Iron tips vs Diamond tips are very different)
- Add CV report integration once Phase 2 clip analysis is built
