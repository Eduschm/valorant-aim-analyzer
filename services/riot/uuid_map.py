"""Agent and weapon UUID → display name resolver with 24h disk cache.

Maps are loaded once per process (lazy, on first resolve call) from disk cache.
Falls back to UUID passthrough on network failure or cache miss — never fatal.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import httpx

CACHE_DIR   = Path(__file__).parent / ".cache"
AGENTS_CACHE  = CACHE_DIR / "agents.json"
WEAPONS_CACHE = CACHE_DIR / "weapons.json"
TTL_SECONDS   = 86_400  # 24h

AGENTS_URL  = "https://valorant-api.com/v1/agents"
WEAPONS_URL = "https://valorant-api.com/v1/weapons"

# Module-level maps populated on first resolve call
_agent_map:  dict[str, str] = {}
_weapon_map: dict[str, str] = {}
_maps_loaded = False


def _load_or_fetch(cache_path: Path, fetch_fn) -> dict[str, str]:
    """Return cached data if fresh (< 24h); otherwise fetch, cache, and return.
    Returns empty dict on network failure — callers fall back to UUID passthrough."""
    if cache_path.exists():
        try:
            with cache_path.open() as fh:
                data = json.load(fh)
            if time.time() - data.get("_ts", 0) < TTL_SECONDS:
                return {k: v for k, v in data.items() if k != "_ts"}
        except (json.JSONDecodeError, OSError):
            pass

    try:
        result = fetch_fn()
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        payload: dict = dict(result)
        payload["_ts"] = time.time()
        with cache_path.open("w") as fh:
            json.dump(payload, fh)
        return result
    except Exception:
        return {}


def _fetch_agents() -> dict[str, str]:
    resp = httpx.get(AGENTS_URL, timeout=10.0)
    resp.raise_for_status()
    return {
        a["uuid"].lower(): a["displayName"]
        for a in resp.json().get("data", [])
        if a.get("uuid") and a.get("displayName")
    }


def _fetch_weapons() -> dict[str, str]:
    resp = httpx.get(WEAPONS_URL, timeout=10.0)
    resp.raise_for_status()
    return {
        w["uuid"].lower(): w["displayName"]
        for w in resp.json().get("data", [])
        if w.get("uuid") and w.get("displayName")
    }


def load_maps() -> None:
    """Populate module-level agent/weapon maps. Non-fatal on network failure."""
    global _agent_map, _weapon_map, _maps_loaded
    _agent_map  = _load_or_fetch(AGENTS_CACHE, _fetch_agents)
    _weapon_map = _load_or_fetch(WEAPONS_CACHE, _fetch_weapons)
    _maps_loaded = True


def resolve_agent(uuid: str) -> str:
    """Resolve agent UUID to display name. Returns UUID unchanged on cache miss."""
    global _maps_loaded
    if not _maps_loaded:
        load_maps()
    return _agent_map.get(uuid.lower(), uuid)


def resolve_weapon(uuid: str) -> str:
    """Resolve weapon UUID to display name. Returns UUID unchanged on cache miss."""
    global _maps_loaded
    if not _maps_loaded:
        load_maps()
    return _weapon_map.get(uuid.lower(), uuid)
