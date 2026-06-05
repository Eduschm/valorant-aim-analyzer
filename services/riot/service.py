"""Public entry point for the riot service."""

from __future__ import annotations

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from contracts.schemas import RiotReport
from services.logging import configure_logging, get_logger
from .client import RiotClient, RiotAPIError
from .parser import parse_match, parse_rank, build_riot_report

configure_logging()
logger = get_logger("services.riot.service")

# Regions probed in order when no explicit region is given.
# Covers all Riot routing clusters: americas (na), europe (eu), asia (ap/kr).
PROBE_REGIONS = ["na", "eu", "ap", "kr"]


async def _build_redis_client():
    """Return an async Redis client if REDIS_URL is set, else None."""
    redis_url = os.getenv("REDIS_URL", "")
    if not redis_url:
        return None
    try:
        import redis.asyncio as aioredis
        return aioredis.from_url(redis_url, decode_responses=False)
    except Exception as exc:
        logger.warning("Redis unavailable: %s — match caching disabled", exc)
        return None


async def get_riot_report(riot_id: str, region: str | None = None, match_count: int = 20) -> RiotReport:
    """
    Full pipeline: "Name#TAG" → RiotReport.

    When region is None, probes na → eu → ap → kr in order until PUUID resolves.
    Resolved region is stored in RiotReport.region.
    Raises RiotAPIError if the Riot ID doesn't exist in any region or the API key is invalid.
    """
    if "#" not in riot_id:
        raise ValueError(f"Invalid Riot ID format: '{riot_id}'. Expected 'Name#TAG'.")

    logger.info("Fetching Riot report for %s", riot_id)
    game_name, tag_line = riot_id.split("#", 1)

    redis_client = await _build_redis_client()

    # ------------------------------------------------------------------ #
    # Region auto-detection: probe regions until PUUID resolves            #
    # ------------------------------------------------------------------ #
    regions_to_try = [region] if region else PROBE_REGIONS
    puuid: str | None = None
    resolved_region = regions_to_try[0]
    last_error: RiotAPIError | None = None

    for probe_region in regions_to_try:
        try:
            async with RiotClient(probe_region, redis_client=redis_client) as probe:
                puuid = await probe.get_puuid(game_name, tag_line)
            resolved_region = probe_region
            logger.debug("PUUID resolved in region=%s for %s", resolved_region, riot_id)
            break
        except RiotAPIError as exc:
            if exc.status in (403, 404):
                last_error = exc
                logger.debug("PUUID not found in region=%s (HTTP %d), trying next", probe_region, exc.status)
                continue
            raise  # unexpected errors propagate immediately

    if puuid is None:
        raise last_error or RiotAPIError(404, f"Riot ID '{riot_id}' not found in any region")

    # ------------------------------------------------------------------ #
    # Fetch matches + rank using the resolved region                       #
    # ------------------------------------------------------------------ #
    async with RiotClient(resolved_region, redis_client=redis_client) as client:
        match_ids = await client.get_match_ids(puuid, count=match_count)

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

        raw_rank  = await client.get_rank(game_name, tag_line)
        rank_data = parse_rank(raw_rank)

    if redis_client is not None:
        try:
            await redis_client.aclose()
        except Exception:
            pass

    report = build_riot_report(puuid, game_name, tag_line, matches, rank_data, resolved_region)
    logger.info("Built RiotReport for %s with %d matches in region=%s", riot_id, len(matches), resolved_region)
    return report
