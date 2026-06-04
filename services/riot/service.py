"""Public entry point for the riot service."""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from contracts.schemas import RiotReport
from services.logging import configure_logging, get_logger
from .client import RiotClient, RiotAPIError
from .parser import parse_match, parse_rank, build_riot_report

configure_logging()
logger = get_logger("services.riot.service")


async def get_riot_report(riot_id: str, region: str = "na", match_count: int = 20) -> RiotReport:
    """
    Full pipeline: "Name#TAG" → RiotReport.
    Raises RiotAPIError if the Riot ID doesn't exist or the API key is invalid.
    """
    if "#" not in riot_id:
        raise ValueError(f"Invalid Riot ID format: '{riot_id}'. Expected 'Name#TAG'.")

    logger.info("Fetching Riot report for %s", riot_id)
    game_name, tag_line = riot_id.split("#", 1)

    async with RiotClient(region) as client:
        # 1. Resolve PUUID
        puuid = await client.get_puuid(game_name, tag_line)
        logger.debug("Resolved puuid=%s for %s", puuid, riot_id)

        # 2. Fetch match IDs
        match_ids = await client.get_match_ids(puuid, count=match_count)

        # 3. Fetch each match and parse
        matches = []
        for mid in match_ids:
            try:
                raw = await client.get_match(mid)
                stat = parse_match(raw, puuid)
                if stat:
                    matches.append(stat)
            except RiotAPIError:
                logger.warning("Skipping match %s due to RiotAPIError", mid)
                continue

        # 4. Fetch rank (non-fatal — Henrik API is unofficial)
        raw_rank  = await client.get_rank(game_name, tag_line)
        rank_data = parse_rank(raw_rank)

    report = build_riot_report(puuid, game_name, tag_line, matches, rank_data)
    logger.info("Built RiotReport for %s with %d matches", riot_id, len(matches))
    return report
