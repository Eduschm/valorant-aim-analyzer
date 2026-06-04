# Riot Service

## Status: ✅ DONE

Full implementation exists. No stubs remain.

---

## What's built

| File | Purpose |
|---|---|
| `client.py` | Async HTTP client — `get_puuid`, `get_match_ids`, `get_match`, `get_rank` |
| `parser.py` | JSON parsing — `parse_match`, `parse_rank`, `build_riot_report` |
| `service.py` | Public entry point — `get_riot_report(riot_id, region, match_count)` |
| `tests/test_parser.py` | 8 gate tests, all mocked, no real API calls |

---

## How to use

```python
from services.riot.service import get_riot_report

riot = await get_riot_report("PlayerName#NA1", region="na")
# → RiotReport (contracts/schemas.py)
```

---

## Running tests

```bash
cd valorant-aim-analyzer
pytest services/riot/tests/ -v
```

---

## Known limitations

1. **Weapon extraction** — Riot match-v1 doesn't expose weapon stats directly in player objects.
   `parser.py` extracts from `roundResults[].playerStats[].kills[].finishingDamage.damageItem`.
   This is a weapon UUID, not a human name. Map to names via Valorant content API if needed.

2. **ADR approximation** — Riot doesn't expose damage per round in match-v1.
   We use `score / numberOfRounds` as a proxy. Not exact but directionally correct.

3. **Region routing** — Default is `na`. Pass `region="eu"` etc. to change.
   Region must match where the account was created, not where the player is currently.

4. **Dev key expiry** — `RIOT_API_KEY` dev keys expire every 24h.
   Apply for a production key at https://developer.riotgames.com/app-type before going live.

---

## Remaining improvements (optional, not blocking)

- Map agent UUIDs to human names via `https://valorant-api.com/v1/agents`
- Map weapon UUIDs to human names via `https://valorant-api.com/v1/weapons`
- Add Redis caching for match data (same match fetched by multiple users)
- Handle region auto-detection from Riot ID (query multiple regions if first fails)
