# LLM Service

Generates personalized Valorant coaching reports using Claude.

## Quick Start

```python
from services.llm.coach import generate_coaching_report
from contracts.schemas import RiotReport

riot = RiotReport(...)  # from riot service
cv = None  # or CVReport from cv service

coaching = await generate_coaching_report(riot, cv)
print(coaching.summary)
```

## Architecture

- **Entry point**: `coach.py` — Main `generate_coaching_report()` function
- **Prompt builder**: `build_prompt()` — Constructs the coaching prompt from Riot + CV data
- **Contracts**: Imports from `contracts/schemas.py` (RiotReport, CoachingReport)

## Data Flow

```
generate_coaching_report(riot_report, cv_report=None)
  ↓
build_prompt(riot_report, cv_report)  # Construct LLM prompt
  ↓
client.messages.create(
  model="claude-haiku-4-5",
  messages=[{"role": "user", "content": prompt}]
)
  ↓
Parse JSON from response
  ↓
CoachingReport(summary, tips, etc.)
```

## Configuration

Via `.env`:
- `ANTHROPIC_API_KEY` — Claude API key (required)
- `LLM_MODEL` — Model to use (default: "claude-haiku-4-5")
- `LOG_LEVEL` — Logging level (default: INFO)

## Dependencies

- anthropic — Claude API client
- python-dotenv — environment config

## Testing

```bash
python -m pytest services/llm/tests/ -v
```

Tests mock `anthropic.Anthropic` and validate:
- Prompt construction
- JSON parsing
- Retry logic on invalid JSON
- Markdown fence stripping

## Error Handling

- **ValueError**: Raised if `ANTHROPIC_API_KEY` not set
- **json.JSONDecodeError**: Claude response malformed
  - Auto-retry once with explicit nudge to return valid JSON
  - If retry fails, raise error (logged, handled by API)

## Cost

~$0.006 per analysis call (Claude Haiku 4.5).

## Response Format

CoachingReport contains:
- `summary` — 2-3 sentence overview
- `top_weakness` — Primary area for improvement
- `tips` — List of actionable tips
- `encouragement` — Motivational message
- `raw_response` — Full LLM output (for debugging)
