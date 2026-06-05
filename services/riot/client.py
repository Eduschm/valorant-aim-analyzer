"""Riot Games + Henrik Dev API async HTTP client."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

load_dotenv()

RIOT_API_KEY   = os.getenv("RIOT_API_KEY", "")
HENRIK_API_KEY = os.getenv("HENRIK_API_KEY", "")

MATCH_CACHE_TTL = 86_400  # 24h — match data never changes after a game ends

REGIONS = {
    "na":    "americas",
    "br":    "americas",
    "latam": "americas",
    "eu":    "europe",
    "ap":    "asia",
    "kr":    "asia",
}

# Riot uses region-specific hostnames for Valorant match endpoints
MATCH_HOSTS = {
    "na":    "na.api.riotgames.com",
    "br":    "br.api.riotgames.com",
    "latam": "la.api.riotgames.com",
    "eu":    "eu.api.riotgames.com",
    "ap":    "ap.api.riotgames.com",
    "kr":    "kr.api.riotgames.com",
}


class RiotAPIError(Exception):
    def __init__(self, status: int, message: str):
        self.status  = status
        self.message = message
        super().__init__(f"Riot API {status}: {message}")


class RiotClient:
    """
    Async HTTP client for Riot + Henrik Dev APIs.
    All public methods raise RiotAPIError on non-2xx.
    Use as an async context manager:
        async with RiotClient("na") as client:
            puuid = await client.get_puuid("Name", "TAG")

    Pass redis_client to enable match caching (TTL 24h). When absent, every
    call hits the Riot API directly. Non-fatal: Redis errors are swallowed.
    """

    def __init__(self, region: str = "na", redis_client=None):
        self.region      = region.lower()
        self.routing     = REGIONS.get(self.region, "americas")
        self.match_host  = MATCH_HOSTS.get(self.region, "na.api.riotgames.com")
        self._headers    = {"X-Riot-Token": RIOT_API_KEY}
        self._client     = httpx.AsyncClient(timeout=15.0)
        self._redis      = redis_client

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.TransportError),
        reraise=True,
    )
    async def _get(self, url: str, headers: dict | None = None) -> dict:
        h = {**self._headers, **(headers or {})}
        resp = await self._client.get(url, headers=h)
        if resp.status_code == 429:
            raise RiotAPIError(429, "Rate limited — back off and retry")
        if resp.status_code >= 400:
            raise RiotAPIError(resp.status_code, resp.text[:200])
        return resp.json()

    # ------------------------------------------------------------------
    # Account
    # ------------------------------------------------------------------

    async def get_puuid(self, game_name: str, tag_line: str) -> str:
        """Resolve Riot ID → PUUID via Account-v1."""
        url = (
            f"https://{self.routing}.api.riotgames.com"
            f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        )
        data = await self._get(url)
        return data["puuid"]

    # ------------------------------------------------------------------
    # Match history
    # ------------------------------------------------------------------

    async def get_match_ids(self, puuid: str, count: int = 20) -> list[str]:
        """Fetch last `count` Valorant match IDs for a PUUID."""
        url = (
            f"https://{self.match_host}"
            f"/val/match/v1/matchlists/by-puuid/{puuid}"
        )
        data = await self._get(url)
        history = data.get("history", [])
        return [m["matchId"] for m in history[:count]]

    async def get_match(self, match_id: str) -> dict[str, Any]:
        """Fetch full match data for a match ID. Returns cached result if available."""
        cache_key = f"match:{match_id}"

        if self._redis is not None:
            try:
                cached = await self._redis.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass  # Redis failure is non-fatal

        url = f"https://{self.match_host}/val/match/v1/matches/{match_id}"
        data = await self._get(url)

        if self._redis is not None:
            try:
                await self._redis.setex(cache_key, MATCH_CACHE_TTL, json.dumps(data))
            except Exception:
                pass

        return data

    # ------------------------------------------------------------------
    # Rank / MMR  (Henrik Dev — no Riot key needed)
    # ------------------------------------------------------------------

    async def get_rank(self, game_name: str, tag_line: str) -> dict[str, Any]:
        """
        Fetch current rank + MMR history via Henrik Dev API.
        https://docs.henrikdev.xyz/valorant/api-reference/mmr
        """
        headers = {}
        if HENRIK_API_KEY:
            headers["Authorization"] = HENRIK_API_KEY

        url = (
            f"https://api.henrikdev.xyz/valorant/v2/mmr"
            f"/{self.region}/{game_name}/{tag_line}"
        )
        try:
            resp = await self._client.get(url, headers=headers, timeout=10.0)
            if resp.status_code >= 400:
                # Henrik errors are non-fatal — return empty dict, rank shown as Unknown
                return {}
            return resp.json()
        except httpx.TransportError:
            return {}

    async def close(self):
        await self._client.aclose()
