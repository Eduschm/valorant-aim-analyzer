"""Gate tests for services/riot/names.py — no real network calls."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import json
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from services.riot.names import (
    AGENTS_CACHE,
    WEAPONS_CACHE,
    _cache_valid,
    _load,
    _save,
    get_agent_names,
    get_weapon_names,
)

FIXTURE_AGENTS_RESPONSE = {
    "data": [
        {"uuid": "f94c3b30-42be-11eb-aa36-3da539379e06", "displayName": "Jett"},
        {"uuid": "7f94d92c-4234-0a36-9646-3a87eb8b5ebd", "displayName": "Sage"},
    ]
}

FIXTURE_WEAPONS_RESPONSE = {
    "data": [
        {"uuid": "9c82e19d-4575-0200-1a81-3eacf00cf872", "displayName": "Vandal"},
        {"uuid": "ae3de142-4d85-2547-dd26-4e90bed35cf7", "displayName": "Phantom"},
    ]
}

FIXTURE_AGENT_MAP  = {a["uuid"]: a["displayName"] for a in FIXTURE_AGENTS_RESPONSE["data"]}
FIXTURE_WEAPON_MAP = {w["uuid"]: w["displayName"] for w in FIXTURE_WEAPONS_RESPONSE["data"]}


def _mock_httpx_response(json_data: dict) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    return resp


# ------------------------------------------------------------------ helpers


def test_cache_valid_returns_false_when_missing(tmp_path):
    assert _cache_valid(tmp_path / "nonexistent.json") is False


def test_cache_valid_returns_false_when_stale(tmp_path):
    p = tmp_path / "stale.json"
    p.write_text("{}")
    # backdate mtime by 2 days
    old_time = time.time() - 2 * 86_400
    os.utime(p, (old_time, old_time))
    assert _cache_valid(p) is False


def test_cache_valid_returns_true_when_fresh(tmp_path):
    p = tmp_path / "fresh.json"
    p.write_text("{}")
    assert _cache_valid(p) is True


def test_save_and_load_roundtrip(tmp_path):
    p = tmp_path / "data.json"
    _save(p, {"key": "value"})
    assert _load(p) == {"key": "value"}


# ------------------------------------------------------------------ get_agent_names


@pytest.mark.asyncio
async def test_get_agent_names_fetches_from_api_when_no_cache(tmp_path, monkeypatch):
    monkeypatch.setattr("services.riot.names.AGENTS_CACHE", tmp_path / "agents.json")
    monkeypatch.setattr("services.riot.names.CACHE_DIR",    tmp_path)

    mock_resp = _mock_httpx_response(FIXTURE_AGENTS_RESPONSE)
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_resp)):
        names = await get_agent_names()

    assert names["f94c3b30-42be-11eb-aa36-3da539379e06"] == "Jett"
    assert names["7f94d92c-4234-0a36-9646-3a87eb8b5ebd"] == "Sage"


@pytest.mark.asyncio
async def test_get_agent_names_uses_cache_when_valid(tmp_path, monkeypatch):
    cache_path = tmp_path / "agents.json"
    _save(cache_path, FIXTURE_AGENT_MAP)
    monkeypatch.setattr("services.riot.names.AGENTS_CACHE", cache_path)

    # No HTTP mock — if network is hit the test will fail with a real request
    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=AssertionError("should not call network"))):
        names = await get_agent_names()

    assert names == FIXTURE_AGENT_MAP


# ------------------------------------------------------------------ get_weapon_names


@pytest.mark.asyncio
async def test_get_weapon_names_fetches_from_api_when_no_cache(tmp_path, monkeypatch):
    monkeypatch.setattr("services.riot.names.WEAPONS_CACHE", tmp_path / "weapons.json")
    monkeypatch.setattr("services.riot.names.CACHE_DIR",     tmp_path)

    mock_resp = _mock_httpx_response(FIXTURE_WEAPONS_RESPONSE)
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_resp)):
        names = await get_weapon_names()

    assert names["9c82e19d-4575-0200-1a81-3eacf00cf872"] == "Vandal"


@pytest.mark.asyncio
async def test_get_weapon_names_uses_cache_when_valid(tmp_path, monkeypatch):
    cache_path = tmp_path / "weapons.json"
    _save(cache_path, FIXTURE_WEAPON_MAP)
    monkeypatch.setattr("services.riot.names.WEAPONS_CACHE", cache_path)

    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=AssertionError("should not call network"))):
        names = await get_weapon_names()

    assert names == FIXTURE_WEAPON_MAP
