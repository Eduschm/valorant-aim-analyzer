"""
Resolve Valorant agent/weapon UUIDs → human-readable names.

Maps are fetched from valorant-api.com on first use and cached on disk for 24h.
Falls back to the raw UUID on any failure — always non-fatal.

Tests should set `_maps_loaded = True` and populate `_agent_map` / `_weapon_map`
directly to avoid network calls:

    import services.riot.uuid_map as m
    m._maps_loaded = True
    m._agent_map = {"<uuid>": "Jett"}
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import httpx
from services.logging import get_logger

logger = get_logger("services.riot.uuid_map")

_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
_TTL_SECONDS = 86400  # 24 hours
_FETCH_TIMEOUT = 5    # seconds — short so tests and cold starts don't stall

_agent_map: dict[str, str] = {}
_weapon_map: dict[str, str] = {}
_maps_loaded: bool = False


def _cache_path(name: str) -> str:
    return os.path.join(_CACHE_DIR, f"{name}.json")


def _load_from_cache(name: str) -> dict[str, str] | None:
    path = _cache_path(name)
    try:
        if not os.path.exists(path):
            return None
        if time.time() - os.path.getmtime(path) > _TTL_SECONDS:
            return None
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def _save_to_cache(name: str, data: dict[str, str]) -> None:
    os.makedirs(_CACHE_DIR, exist_ok=True)
    try:
        with open(_cache_path(name), "w") as f:
            json.dump(data, f)
    except OSError as exc:
        logger.warning("Could not write %s cache: %s", name, exc)


def _fetch_agent_map() -> dict[str, str]:
    cached = _load_from_cache("agents")
    if cached is not None:
        return cached
    try:
        with httpx.Client(timeout=_FETCH_TIMEOUT) as client:
            resp = client.get("https://valorant-api.com/v1/agents")
            resp.raise_for_status()
            data = resp.json().get("data", [])
        result = {
            item["uuid"].lower(): item["displayName"]
            for item in data
            if item.get("isPlayableCharacter", True)
        }
        _save_to_cache("agents", result)
        logger.debug("Loaded %d agent entries from valorant-api.com", len(result))
        return result
    except Exception as exc:
        logger.warning("Could not fetch agent map: %s — using empty map (UUID passthrough)", exc)
        return {}


def _fetch_weapon_map() -> dict[str, str]:
    cached = _load_from_cache("weapons")
    if cached is not None:
        return cached
    try:
        with httpx.Client(timeout=_FETCH_TIMEOUT) as client:
            resp = client.get("https://valorant-api.com/v1/weapons")
            resp.raise_for_status()
            data = resp.json().get("data", [])
        result = {item["uuid"].lower(): item["displayName"] for item in data}
        _save_to_cache("weapons", result)
        logger.debug("Loaded %d weapon entries from valorant-api.com", len(result))
        return result
    except Exception as exc:
        logger.warning("Could not fetch weapon map: %s — using empty map (UUID passthrough)", exc)
        return {}


def _ensure_loaded() -> None:
    global _agent_map, _weapon_map, _maps_loaded
    if _maps_loaded:
        return
    _agent_map = _fetch_agent_map()
    _weapon_map = _fetch_weapon_map()
    _maps_loaded = True


def resolve_agent(uuid: str) -> str:
    """Return human-readable agent name, or uuid unchanged if not found."""
    _ensure_loaded()
    return _agent_map.get(uuid.lower(), uuid)


def resolve_weapon(uuid: str) -> str:
    """Return human-readable weapon name, or uuid unchanged if not found."""
    _ensure_loaded()
    return _weapon_map.get(uuid.lower(), uuid)
