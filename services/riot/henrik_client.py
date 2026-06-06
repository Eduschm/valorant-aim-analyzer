"""HenrikDev API async HTTP client.

HenrikDev (https://api.henrikdev.xyz) is a community Valorant API that serves
match history, MMR, and account data without a production Riot key. It requires
a free API key (https://docs.henrikdev.xyz/valorant/changes/v4.0.0), passed in
the Authorization header.

This is the working match-data path: personal/dev Riot keys 403 on val/match/v1,
but Henrik returns full match data (real damage/ADR, human-readable agent names,
competitive tier) for any public account.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

load_dotenv()

HENRIK_API_KEY = os.getenv("HENRIK_API_KEY", "")
HENRIK_BASE = "https://api.henrikdev.xyz"

# Henrik uses "affinity" codes that match our region slugs directly.
VALID_AFFINITIES = {"na", "eu", "ap", "kr", "latam", "br"}


class HenrikAPIError(Exception):
    """Raised on a non-2xx Henrik response. `status` is the HTTP status code so
    the API layer's _friendly_error() can map it to a clear message."""

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"Henrik API {status}: {message}")


class HenrikClient:
    """
    Async HTTP client for the HenrikDev Valorant API.
    All public methods raise HenrikAPIError on non-2xx.

        async with HenrikClient("na") as client:
            acct = await client.get_account("TenZ", "0505")
            mmr = await client.get_mmr("TenZ", "0505")
            matches = await client.get_matches("TenZ", "0505", size=20)
    """

    def __init__(self, region: str = "na", platform: str = "pc"):
        self.region = region.lower()
        self.affinity = self.region if self.region in VALID_AFFINITIES else "na"
        self.platform = platform
        headers = {"Accept": "application/json"}
        # Read at instantiation time, not import time, so .env changes take
        # effect without a full module reload.
        key = os.getenv("HENRIK_API_KEY", "") or HENRIK_API_KEY
        if key:
            headers["Authorization"] = key
        self._client = httpx.AsyncClient(timeout=20.0, headers=headers)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close()

    # ------------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        retry=retry_if_exception_type(httpx.TransportError),
        reraise=True,
    )
    async def _get(self, path: str, params: dict | None = None) -> dict:
        resp = await self._client.get(f"{HENRIK_BASE}{path}", params=params)
        if resp.status_code == 429:
            raise HenrikAPIError(429, "Rate limited — back off and retry")
        if resp.status_code >= 400:
            raise HenrikAPIError(resp.status_code, resp.text[:200])
        return resp.json()

    # ------------------------------------------------------------------
    # Endpoints
    # ------------------------------------------------------------------

    async def get_account(self, game_name: str, tag_line: str) -> dict[str, Any]:
        """Resolve Riot ID → account data (puuid, region). v1/account."""
        data = await self._get(f"/valorant/v1/account/{game_name}/{tag_line}")
        return data.get("data", {})

    async def get_mmr(self, game_name: str, tag_line: str) -> dict[str, Any]:
        """Fetch current MMR / rank. v3/mmr."""
        data = await self._get(
            f"/valorant/v3/mmr/{self.affinity}/{self.platform}/{game_name}/{tag_line}"
        )
        return data.get("data", {})

    async def get_matches(
        self, game_name: str, tag_line: str, mode: str = "competitive", size: int = 20
    ) -> list[dict[str, Any]]:
        """Fetch recent matches with full per-player stats. v4/matches."""
        params: dict[str, Any] = {"size": size}
        if mode:
            params["mode"] = mode
        data = await self._get(
            f"/valorant/v4/matches/{self.affinity}/{self.platform}/{game_name}/{tag_line}",
            params=params,
        )
        return data.get("data", [])

    async def close(self):
        await self._client.aclose()
