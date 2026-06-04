# Riot Service

Fetches Valorant player statistics from the Riot API.

## Quick Start

```python
from services.riot.service import get_riot_report

# Async function
report = await get_riot_report("PlayerName#NA1")
print(report.current_rank, report.avg_headshot_pct)
```

## Architecture

- **Entry point**: `service.py` — Main `get_riot_report()` function
- **Client**: `client.py` — RiotClient with retry logic and error handling
- **Parser**: `parser.py` — Converts raw Riot API responses to typed structures
- **Contracts**: Imports from `contracts/schemas.py` (RiotReport)

## Data Flow

```
get_riot_report(riot_id)
  ↓
RiotClient.get_puuid(game_name, tag_line)
  ↓
RiotClient.get_match_ids(puuid)
  ↓
For each match_id:
  RiotClient.get_match(match_id) → parse_match()
  ↓
RiotClient.get_rank(game_name, tag_line) → parse_rank()
  ↓
build_riot_report() → RiotReport
```

## Configuration

Via `.env`:
- `RIOT_API_KEY` — Riot API key (required)
- `RIOT_REGION` — Region routing (default: "na")
- `LOG_LEVEL` — Logging level (default: INFO)

## Dependencies

- httpx — async HTTP client with retry logic (tenacity)
- tenacity — exponential backoff for rate limit handling
- python-dotenv — environment config

## Testing

```bash
python -m pytest services/riot/tests/ -v
```

Tests mock httpx responses and validate:
- PUUID resolution
- Match fetching and parsing
- Rank fetching (non-fatal failures)
- Error handling and retry logic

## Error Handling

- **RiotAPIError**: Raised on API errors (404, 429, 500)
  - 429 (rate limit): Retried with exponential backoff
  - 500: Silently skipped for match fetches, non-fatal for rank
  - 404: Skipped for match fetches (old matches may be deleted)
- **ValueError**: Invalid Riot ID format (must be `Name#TAG`)

## Rate Limiting

Uses tenacity with:
- Max 3 attempts
- Exponential backoff (1s → 2s → 4s)
- Jitter to prevent thundering herd
