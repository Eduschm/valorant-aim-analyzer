# Riot Service — Agent Implementation Task

## Context
This service fetches Valorant match history and rank data for a given Riot ID,
returning a structured `RiotReport` (defined in `contracts/schemas.py`).

This is a **high-complexity task** — it involves:
- Multiple chained async API calls
- Rate limit handling with exponential backoff
- Parsing a complex nested JSON schema
- Mapping agent UUIDs to human-readable names

## What exists
- `client.py` — stubbed async HTTP client (implement all `raise NotImplementedError` methods)
- `parser.py` — stubbed parser (implement `parse_match`, `parse_rank`, `build_riot_report`)
- `requirements.txt` — dependencies listed

## What to build

### 1. `client.py` — implement all methods

**`get_puuid(game_name, tag_line) → str`**
```
GET https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}
Headers: X-Riot-Token: {RIOT_API_KEY}
Returns: response["puuid"]
```

**`get_match_ids(puuid, count=20) → list[str]`**
```
GET https://na.api.riotgames.com/val/match/v1/matchlists/by-puuid/{puuid}
Headers: X-Riot-Token: {RIOT_API_KEY}
Returns: response["history"][:count] → list of matchId strings
```

**`get_match(match_id) → dict`**
```
GET https://na.api.riotgames.com/val/match/v1/matches/{matchId}
Headers: X-Riot-Token: {RIOT_API_KEY}
Returns: full match JSON
```

**`get_rank(game_name, tag_line) → dict`**
```
GET https://api.henrikdev.xyz/valorant/v2/mmr/{region}/{name}/{tag}
Headers: Authorization: {HENRIK_API_KEY}  (optional)
Returns: rank + MMR history
```

Add `@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))`
to all methods. Raise `RiotAPIError` on 4xx/5xx.

### 2. `parser.py` — implement all functions

**`parse_match(raw_match, puuid) → MatchStat | None`**

Find the player in `raw_match["players"]` where `player["puuid"] == puuid`.

Extract:
```python
kills      = player["stats"]["kills"]
deaths     = player["stats"]["deaths"]
assists    = player["stats"]["assists"]
headshots  = player["stats"]["headshots"]
bodyshots  = player["stats"]["bodyshots"]
legshots   = player["stats"]["legshots"]
total_shots = headshots + bodyshots + legshots
hs_pct     = (headshots / total_shots * 100) if total_shots > 0 else 0

# ADR: Riot doesn't expose damage directly in match-v1.
# Approximate: combat_score / rounds_played
# Or use score as proxy: score / 200 (rough)

agent_id   = player["characterId"]   # UUID, resolve via Valorant content API
weapon     = "Unknown"               # not in match-v1, pull from round results

# Team win/loss
team_id    = player["teamId"]
team       = next(t for t in raw_match["teams"] if t["teamId"] == team_id)
won        = team["won"]
```

**`parse_rank(raw_rank) → dict`**

From Henrik response:
```python
current_tier_name = raw_rank["data"]["current_data"]["currenttierpatched"]
mmr_change        = raw_rank["data"]["current_data"]["mmr_change_to_last_game"]
return {"rank": current_tier_name, "rank_delta": mmr_change}
```

**`build_riot_report(...) → RiotReport`**

Aggregate the match list:
- `avg_headshot_pct` = mean of all match HS%
- `avg_adr` = mean of all match ADR
- `win_rate` = wins / total_matches
- `top_agent` = most frequent agent
- `top_weapon` = most frequent weapon

### 3. Add `service.py` — public entry point

```python
async def get_riot_report(riot_id: str) -> RiotReport:
    """
    Full pipeline: Riot ID → RiotReport.
    Handles: split riot_id on '#', fetch PUUID, fetch 20 matches, parse, rank.
    """
```

### 4. Add `tests/test_parser.py`

Test `parse_match` with a fixture JSON file (record one real match response).
Test edge cases: player not in match, zero shots fired, 0 matches.

## Important constraints
- Region routing: NA → `na.api.riotgames.com`, BR → `br.api.riotgames.com`.
  Use the `REGIONS` dict in `client.py`. Default to NA for MVP.
- Do NOT cache match data in files — use Redis if caching is needed.
- Apply for Riot production key early. Dev key expires every 24h.
- Read Riot API ToS: https://developer.riotgames.com/policies/general
  Do NOT use any game client interaction. Only public match data APIs.

## Done criteria
- `get_riot_report("Shroud#1234")` returns a populated `RiotReport` with no errors
- All stubs replaced, no `raise NotImplementedError` remains
- `pytest services/riot/tests/` passes with fixture data
