"""Public entry point for the riot service."""

from __future__ import annotations

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from contracts.schemas import RiotReport
from services.logging import configure_logging, get_logger
from .client import RiotClient, RiotAPIError
from .names import get_agent_names, get_weapon_names
from .parser import parse_match, parse_rank, build_riot_report

configure_logging()
logger = get_logger("services.riot.service")

# Regions tried in order when no explicit region is given
REGION_CANDIDATES = ["na", "eu", "ap", "kr"]


async def get_riot_report(
    riot_id: str,
    region: str | None = None,
    match_count: int = 20,
) -> RiotReport:
    """
    Full pipeline: "Name#TAG" → RiotReport.

    When `region` is None the service tries na, eu, ap, kr in order and stops
    at the first successful PUUID lookup. The resolved region is stored in
    RiotReport.region.

    Raises RiotAPIError if the Riot ID can't be found in any region.
    """
    if "#" not in riot_id:
        raise ValueError(f"Invalid Riot ID format: '{riot_id}'. Expected 'Name#TAG'.")

    logger.info("Fetching Riot report for %s", riot_id)
    game_name, tag_line = riot_id.split("#", 1)

    regions_to_try = [region] if region else REGION_CANDIDATES
    resolved_region: str | None = None
    matches = []
    rank_data: dict = {}
    last_error: RiotAPIError | None = None

    for r in regions_to_try:
        try:
            async with RiotClient(r) as client:
                puuid = await client.get_puuid(game_name, tag_line)
                resolved_region = r
                logger.debug("Resolved puuid=%s for %s in region=%s", puuid, riot_id, r)

                match_ids = await client.get_match_ids(puuid, count=match_count)

                for mid in match_ids:
                    try:
                        raw  = await client.get_match(mid)
                        stat = parse_match(raw, puuid)
                        if stat:
                            matches.append(stat)
                    except RiotAPIError:
                        logger.warning("Skipping match %s due to RiotAPIError", mid)

                raw_rank  = await client.get_rank(game_name, tag_line)
                rank_data = parse_rank(raw_rank)
            break  # success — exit region loop
        except RiotAPIError as e:
            if e.status in (404, 403):
                last_error = e
                logger.debug("Region %s returned %d for %s, trying next", r, e.status, riot_id)
                continue
            raise  # unexpected error — propagate immediately

    if resolved_region is None:
        raise last_error or RiotAPIError(404, f"Riot ID '{riot_id}' not found in any region")

    # Resolve agent/weapon UUIDs → human-readable names (non-fatal)
    try:
        agent_names, weapon_names = await asyncio.gather(
            get_agent_names(), get_weapon_names()
        )
        for m in matches:
            m.agent  = agent_names.get(m.agent,  m.agent)
            m.weapon = weapon_names.get(m.weapon, m.weapon)
    except Exception:
        logger.warning("Failed to resolve agent/weapon names — raw UUIDs will be used")

    report = build_riot_report(puuid, game_name, tag_line, matches, rank_data, region=resolved_region)
    logger.info("Built RiotReport for %s with %d matches, region=%s", riot_id, len(matches), resolved_region)
    return report
