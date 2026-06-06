"""Public entry point for the riot service.

Two match-data providers:
  - "henrik" (default when HENRIK_API_KEY is set): HenrikDev API. Works with a
    free Henrik key and no production Riot key — this is the path that actually
    returns match data.
  - "riot": Riot's own API. Account lookup works on a dev key, but val/match/v1
    returns 403 unless the key has the Valorant product approved.

Override with the MATCH_PROVIDER env var ("henrik" | "riot").
"""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from contracts.schemas import RiotReport
from services.logging import configure_logging, get_logger
from .client import RiotClient, RiotAPIError
from .henrik_client import HenrikClient, HenrikAPIError, HENRIK_API_KEY
from .parser import parse_match, derive_rank, build_riot_report
from .henrik_parser import parse_henrik_match, rank_from_mmr

configure_logging()
logger = get_logger("services.riot.service")


def _resolve_provider() -> str:
    """Pick the match-data provider. Explicit MATCH_PROVIDER wins; otherwise use
    Henrik when a key is available, else fall back to the Riot direct API."""
    explicit = os.getenv("MATCH_PROVIDER", "").strip().lower()
    if explicit in {"henrik", "riot"}:
        return explicit
    return "henrik" if HENRIK_API_KEY else "riot"


async def get_riot_report(riot_id: str, region: str = "na", match_count: int = 20) -> RiotReport:
    """
    Full pipeline: "Name#TAG" → RiotReport.
    Raises RiotAPIError / HenrikAPIError if the account doesn't exist or the API
    key is invalid.
    """
    if "#" not in riot_id:
        raise ValueError(f"Invalid Riot ID format: '{riot_id}'. Expected 'Name#TAG'.")

    provider = _resolve_provider()
    logger.info("Fetching Riot report for %s via provider=%s region=%s", riot_id, provider, region)
    game_name, tag_line = riot_id.split("#", 1)

    if provider == "henrik":
        return await _get_report_henrik(game_name, tag_line, region, match_count)
    return await _get_report_riot(game_name, tag_line, region, match_count)


async def _get_report_henrik(
    game_name: str, tag_line: str, region: str, match_count: int
) -> RiotReport:
    async with HenrikClient(region) as client:
        account = await client.get_account(game_name, tag_line)
        puuid = account.get("puuid", "")
        logger.debug("Henrik resolved puuid=%s for %s#%s", puuid, game_name, tag_line)

        raw_matches = await client.get_matches(game_name, tag_line, size=match_count)
        matches = []
        for raw in raw_matches:
            stat = parse_henrik_match(raw, puuid)
            if stat:
                matches.append(stat)

        # MMR is non-fatal: rank still derivable from match tiers if it fails.
        try:
            mmr = await client.get_mmr(game_name, tag_line)
        except HenrikAPIError as exc:
            logger.warning("Henrik MMR fetch failed (%s) — deriving rank from matches", exc)
            mmr = {}

    rank_data = rank_from_mmr(mmr, matches)
    report = build_riot_report(puuid, game_name, tag_line, matches, rank_data)
    logger.info("Built RiotReport (henrik) for %s#%s with %d matches", game_name, tag_line, len(matches))
    return report


async def _get_report_riot(
    game_name: str, tag_line: str, region: str, match_count: int
) -> RiotReport:
    async with RiotClient(region) as client:
        puuid = await client.get_puuid(game_name, tag_line)
        logger.debug("Riot resolved puuid=%s for %s#%s", puuid, game_name, tag_line)

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

    rank_data = derive_rank(matches)
    report = build_riot_report(puuid, game_name, tag_line, matches, rank_data)
    logger.info("Built RiotReport (riot) for %s#%s with %d matches", game_name, tag_line, len(matches))
    return report
