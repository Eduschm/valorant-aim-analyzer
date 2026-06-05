"""Parse raw Riot API match JSON into typed MatchStat / RiotReport objects."""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from collections import Counter
from contracts.schemas import MatchStat, RiotReport
from .uuid_map import resolve_agent, resolve_weapon


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

    # ADR approximation: combat score / rounds played
    # Riot doesn't expose damage directly in match-v1
    num_rounds = info.get("numberOfRounds", max(info.get("roundsPlayed", 1), 1))
    adr = score / num_rounds if num_rounds > 0 else 0.0

    # Determine if this player's team won
    team_id = player.get("teamId", "")
    team    = next((t for t in teams if t.get("teamId") == team_id), {})
    won     = team.get("won", False)

    # Resolve agent UUID → display name (e.g. "f94c3b30-..." → "Jett")
    agent = resolve_agent(player.get("characterId", "Unknown"))

    # Weapon: not directly in player object; would need round-level data
    # Use the most-used weapon from round stats if available
    weapon = _extract_top_weapon(raw_match, puuid)

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
    )


def _extract_top_weapon(raw_match: dict, puuid: str) -> str:
    """Best-effort weapon extraction from round results."""
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
        top_uuid = weapon_kills.most_common(1)[0][0]
        return resolve_weapon(top_uuid)
    return "Unknown"


def parse_rank(raw_rank: dict) -> dict:
    """
    Extract current rank string and rank_delta from Henrik MMR payload.
    Returns {"rank": str, "rank_delta": int}
    """
    if not raw_rank:
        return {"rank": "Unranked", "rank_delta": 0}

    try:
        data         = raw_rank.get("data", {})
        current      = data.get("current_data", {})
        rank         = current.get("currenttierpatched", "Unranked") or "Unranked"
        rank_delta   = current.get("mmr_change_to_last_game", 0) or 0
        return {"rank": rank, "rank_delta": int(rank_delta)}
    except Exception:
        return {"rank": "Unranked", "rank_delta": 0}


def build_riot_report(
    puuid: str,
    game_name: str,
    tag_line: str,
    matches: list[MatchStat],
    rank_data: dict,
    region: str = "na",
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
            region=region,
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
        region=region,
    )
