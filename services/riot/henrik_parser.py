"""Parse HenrikDev v4 match JSON + v3 MMR JSON into typed MatchStat / rank data.

Henrik's v4 match payload is richer than Riot's match-v1: it exposes real damage
(so real ADR), human-readable agent names, and the player's competitive tier per
match. Tier ids use the same 0-27 scale as Riot's competitiveTier, so the existing
tier_name() / derive_rank() helpers apply.
"""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from collections import Counter
from contracts.schemas import MatchStat
from .parser import tier_name, derive_rank


def parse_henrik_match(match: dict, puuid: str) -> MatchStat | None:
    """Extract one player's MatchStat from a Henrik v4 match payload.
    Returns None if the player is not in the match."""
    metadata = match.get("metadata", {})
    players = match.get("players", [])

    player = next((p for p in players if p.get("puuid") == puuid), None)
    if player is None:
        return None

    stats = player.get("stats", {})
    kills = stats.get("kills", 0)
    deaths = stats.get("deaths", 0)
    assists = stats.get("assists", 0)
    headshots = stats.get("headshots", 0)
    bodyshots = stats.get("bodyshots", 0)
    legshots = stats.get("legshots", 0)
    damage = (stats.get("damage") or {}).get("dealt", 0)

    total_shots = headshots + bodyshots + legshots
    hs_pct = (headshots / total_shots * 100) if total_shots > 0 else 0.0

    rounds_played = _rounds_played(match)
    adr = (damage / rounds_played) if rounds_played > 0 else 0.0

    won = _player_won(match, player.get("team_id", ""))

    agent = (player.get("agent") or {}).get("name") or "Unknown"
    competitive_tier = int((player.get("tier") or {}).get("id", 0) or 0)
    weapon = _top_weapon(match, puuid)
    match_id = metadata.get("match_id", "")

    return MatchStat(
        match_id=match_id,
        agent=agent,
        weapon=weapon,
        kills=kills,
        deaths=deaths,
        assists=assists,
        headshot_pct=round(hs_pct, 1),
        adr=round(adr, 1),
        won=won,
        competitive_tier=competitive_tier,
    )


def _rounds_played(match: dict) -> int:
    rounds = match.get("rounds")
    if isinstance(rounds, list) and rounds:
        return len(rounds)
    # Fallback: sum a team's won + lost rounds.
    for team in match.get("teams", []):
        r = team.get("rounds") or {}
        total = (r.get("won", 0) or 0) + (r.get("lost", 0) or 0)
        if total > 0:
            return total
    return 0


def _player_won(match: dict, team_id: str) -> bool:
    team = next((t for t in match.get("teams", []) if t.get("team_id") == team_id), None)
    return bool(team.get("won", False)) if team else False


def _top_weapon(match: dict, puuid: str) -> str:
    """Most-used weapon by kill count for this player, from match.kills[]."""
    counts: Counter = Counter()
    for kill in match.get("kills", []):
        if (kill.get("killer") or {}).get("puuid") != puuid:
            continue
        name = (kill.get("weapon") or {}).get("name")
        if name:
            counts[name] += 1
    return counts.most_common(1)[0][0] if counts else "Unknown"


def rank_from_mmr(mmr: dict, matches: list[MatchStat]) -> dict:
    """Build {"rank", "rank_delta"} preferring MMR current tier for the rank label,
    and deriving the delta from the fetched matches' competitive tiers."""
    delta = derive_rank(matches).get("rank_delta", 0)

    current = (mmr or {}).get("current") or {}
    tier = current.get("tier") or {}
    name = tier.get("name")
    tid = tier.get("id")
    if name:
        return {"rank": name, "rank_delta": delta}
    if isinstance(tid, int) and tid > 0:
        return {"rank": tier_name(tid), "rank_delta": delta}
    # No usable MMR — fall back to match-derived rank.
    return {"rank": derive_rank(matches).get("rank", "Unranked"), "rank_delta": delta}
