"""Parse raw Riot API match JSON into typed MatchStat / RiotReport objects."""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from collections import Counter
from contracts.schemas import MatchStat, RiotReport
from .uuid_map import resolve_agent, resolve_weapon


# Riot competitiveTier int -> human-readable rank name.
# Tiers 1-2 are unused (legacy); anything unmapped falls back to "Unranked".
TIER_NAMES: dict[int, str] = {
    0:  "Unranked",
    3:  "Iron 1",      4:  "Iron 2",      5:  "Iron 3",
    6:  "Bronze 1",    7:  "Bronze 2",    8:  "Bronze 3",
    9:  "Silver 1",    10: "Silver 2",    11: "Silver 3",
    12: "Gold 1",      13: "Gold 2",      14: "Gold 3",
    15: "Platinum 1",  16: "Platinum 2",  17: "Platinum 3",
    18: "Diamond 1",   19: "Diamond 2",   20: "Diamond 3",
    21: "Ascendant 1", 22: "Ascendant 2", 23: "Ascendant 3",
    24: "Immortal 1",  25: "Immortal 2",  26: "Immortal 3",
    27: "Radiant",
}


def tier_name(tier: int) -> str:
    """Map a Riot competitiveTier integer to a rank label."""
    return TIER_NAMES.get(tier, "Unranked")


def parse_match(raw_match: dict, puuid: str) -> MatchStat | None:
    """
    Extract one player's MatchStat from a raw Riot match payload.
    Returns None if the player is not in this match.
    """
    info    = raw_match.get("matchInfo", {})
    players = raw_match.get("players", [])
    teams   = raw_match.get("teams", [])

    player = next((p for p in players if p.get("puuid") == puuid), None)
    if player is None:
        return None

    stats     = player.get("stats", {})
    kills     = stats.get("kills", 0)
    deaths    = stats.get("deaths", 0)
    assists   = stats.get("assists", 0)
    headshots = stats.get("headshots", 0)
    bodyshots = stats.get("bodyshots", 0)
    legshots  = stats.get("legshots", 0)
    score     = stats.get("score", 0)

    total_shots = headshots + bodyshots + legshots
    hs_pct = (headshots / total_shots * 100) if total_shots > 0 else 0.0

    # Try real ADR from round-level damage data; fall back to score/rounds approximation.
    real_adr = _extract_real_adr(raw_match, puuid)
    if real_adr is not None:
        adr = real_adr
        adr_is_estimated = False
    else:
        num_rounds = info.get("numberOfRounds", max(info.get("roundsPlayed", 1), 1))
        adr = score / num_rounds if num_rounds > 0 else 0.0
        adr_is_estimated = True

    # Determine if this player's team won
    team_id = player.get("teamId", "")
    team    = next((t for t in teams if t.get("teamId") == team_id), {})
    won     = team.get("won", False)

    # Resolve agent UUID → human name; falls back to UUID if not in the map.
    agent = resolve_agent(player.get("characterId", "Unknown"))

    # Riot exposes the player's rank for the match via competitiveTier
    competitive_tier = int(player.get("competitiveTier", 0) or 0)

    # Weapon: resolve UUID → name from round kill data.
    weapon = resolve_weapon(_extract_top_weapon_uuid(raw_match, puuid))

    match_id = raw_match.get("matchInfo", {}).get("matchId", "")

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
        adr_is_estimated=adr_is_estimated,
    )


def _extract_top_weapon_uuid(raw_match: dict, puuid: str) -> str:
    """Best-effort weapon UUID extraction from round results."""
    rounds = raw_match.get("roundResults", [])
    weapon_kills: Counter = Counter()

    for rnd in rounds:
        for player_stat in rnd.get("playerStats", []):
            if player_stat.get("puuid") != puuid:
                continue
            for kill in player_stat.get("kills", []):
                weapon_id = kill.get("finishingDamage", {}).get("damageItem", "")
                if weapon_id:
                    weapon_kills[weapon_id] += 1

    if weapon_kills:
        return weapon_kills.most_common(1)[0][0]
    return "Unknown"


def _extract_real_adr(raw_match: dict, puuid: str) -> float | None:
    """
    Compute real ADR from roundResults damage arrays.
    Returns None when data is absent, signalling the caller to fall back to
    the score/rounds approximation.
    """
    rounds = raw_match.get("roundResults", [])
    if not rounds:
        return None

    num_rounds = raw_match.get("matchInfo", {}).get("numberOfRounds") or len(rounds)
    if num_rounds == 0:
        return None

    total_damage = 0
    found_any = False
    for rnd in rounds:
        for ps in rnd.get("playerStats", []):
            if ps.get("puuid") != puuid:
                continue
            for dmg in ps.get("damage", []):
                val = dmg.get("damage", 0)
                if val > 0:
                    found_any = True
                total_damage += val

    if not found_any:
        return None  # Riot API stripped damage data for this match

    return round(total_damage / num_rounds, 1)


def derive_rank(matches: list[MatchStat]) -> dict:
    """
    Derive current rank and rank_delta from Riot match data.
    `matches` is newest-first (matches[0] is the most recent game).
    rank_delta is the competitiveTier change from the oldest fetched
    match to the newest (+ = climbed, - = dropped).
    Returns {"rank": str, "rank_delta": int}
    """
    ranked = [m for m in matches if m.competitive_tier > 0]
    if not ranked:
        return {"rank": "Unranked", "rank_delta": 0}

    current_tier = ranked[0].competitive_tier
    rank_delta   = current_tier - ranked[-1].competitive_tier
    return {"rank": tier_name(current_tier), "rank_delta": int(rank_delta)}


def build_riot_report(
    puuid: str,
    game_name: str,
    tag_line: str,
    matches: list[MatchStat],
    rank_data: dict,
) -> RiotReport:
    """Aggregate a list of MatchStat into a RiotReport summary."""
    if not matches:
        return RiotReport(
            puuid=puuid,
            game_name=game_name,
            tag_line=tag_line,
            current_rank=rank_data.get("rank", "Unranked"),
            rank_delta=rank_data.get("rank_delta", 0),
            matches=[],
            avg_headshot_pct=0.0,
            avg_adr=0.0,
            top_agent="Unknown",
            top_weapon="Unknown",
            win_rate=0.0,
        )

    avg_hs  = sum(m.headshot_pct for m in matches) / len(matches)
    avg_adr = sum(m.adr          for m in matches) / len(matches)
    wins    = sum(1 for m in matches if m.won)

    agents  = Counter(m.agent  for m in matches if m.agent  != "Unknown")
    weapons = Counter(m.weapon for m in matches if m.weapon != "Unknown")

    top_agent  = agents.most_common(1)[0][0]  if agents  else "Unknown"
    top_weapon = weapons.most_common(1)[0][0] if weapons else "Unknown"

    return RiotReport(
        puuid=puuid,
        game_name=game_name,
        tag_line=tag_line,
        current_rank=rank_data.get("rank", "Unranked"),
        rank_delta=rank_data.get("rank_delta", 0),
        matches=matches,
        avg_headshot_pct=round(avg_hs, 1),
        avg_adr=round(avg_adr, 1),
        top_agent=top_agent,
        top_weapon=top_weapon,
        win_rate=round(wins / len(matches), 2),
        adr_is_estimated=any(m.adr_is_estimated for m in matches),
    )
