"""Resolve Valorant agent/weapon UUIDs to human-readable names via valorant-api.com."""

from __future__ import annotations

import json
import time
from pathlib import Path

import httpx

CACHE_DIR     = Path(__file__).parent / ".cache"
AGENTS_CACHE  = CACHE_DIR / "agents.json"
WEAPONS_CACHE = CACHE_DIR / "weapons.json"
TTL_SECONDS   = 86_400  # 24 hours

AGENTS_URL  = "https://valorant-api.com/v1/agents"
WEAPONS_URL = "https://valorant-api.com/v1/weapons"


def _cache_valid(path: Path) -> bool:
    return path.exists() and (time.time() - path.stat().st_mtime) < TTL_SECONDS


def _load(path: Path) -> dict[str, str]:
    with open(path) as f:
        return json.load(f)


def _save(path: Path, data: dict[str, str]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)


async def get_agent_names() -> dict[str, str]:
    """Return {uuid: displayName} for all Valorant agents. Cached to disk for 24h."""
    if _cache_valid(AGENTS_CACHE):
        return _load(AGENTS_CACHE)
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(AGENTS_URL)
        resp.raise_for_status()
        data = resp.json()
    names = {a["uuid"]: a["displayName"] for a in data.get("data", [])}
    _save(AGENTS_CACHE, names)
    return names


async def get_weapon_names() -> dict[str, str]:
    """Return {uuid: displayName} for all Valorant weapons. Cached to disk for 24h."""
    if _cache_valid(WEAPONS_CACHE):
        return _load(WEAPONS_CACHE)
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(WEAPONS_URL)
        resp.raise_for_status()
        data = resp.json()
    names = {w["uuid"]: w["displayName"] for w in data.get("data", [])}
    _save(WEAPONS_CACHE, names)
    return names
