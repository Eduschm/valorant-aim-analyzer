"""Gate tests for uuid_map — no real network calls."""

from __future__ import annotations

import json
import time
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest

import services.riot.uuid_map as uuid_map


JETT_UUID   = "f94c3b30-42be-11eb-aa36-3da539379e06"
VANDAL_UUID = "9c82e19d-4575-0200-1a81-3eacf00cf872"


@pytest.fixture(autouse=True)
def reset_maps():
    """Reset module-level maps before each test."""
    orig_agent  = dict(uuid_map._agent_map)
    orig_weapon = dict(uuid_map._weapon_map)
    orig_loaded = uuid_map._maps_loaded
    yield
    uuid_map._agent_map   = orig_agent
    uuid_map._weapon_map  = orig_weapon
    uuid_map._maps_loaded = orig_loaded


def test_resolve_agent_returns_name_when_in_map(monkeypatch):
    monkeypatch.setattr(uuid_map, "_agent_map",  {JETT_UUID: "Jett"})
    monkeypatch.setattr(uuid_map, "_weapon_map", {})
    monkeypatch.setattr(uuid_map, "_maps_loaded", True)
    assert uuid_map.resolve_agent(JETT_UUID) == "Jett"


def test_resolve_agent_returns_uuid_on_miss(monkeypatch):
    monkeypatch.setattr(uuid_map, "_agent_map",  {})
    monkeypatch.setattr(uuid_map, "_maps_loaded", True)
    assert uuid_map.resolve_agent("unknown-uuid") == "unknown-uuid"


def test_resolve_weapon_returns_name_when_in_map(monkeypatch):
    monkeypatch.setattr(uuid_map, "_weapon_map", {VANDAL_UUID: "Vandal"})
    monkeypatch.setattr(uuid_map, "_agent_map",  {})
    monkeypatch.setattr(uuid_map, "_maps_loaded", True)
    assert uuid_map.resolve_weapon(VANDAL_UUID) == "Vandal"


def test_resolve_weapon_returns_uuid_on_miss(monkeypatch):
    monkeypatch.setattr(uuid_map, "_weapon_map", {})
    monkeypatch.setattr(uuid_map, "_maps_loaded", True)
    assert uuid_map.resolve_weapon("unknown-weapon-uuid") == "unknown-weapon-uuid"


def test_uuid_lookup_is_case_insensitive(monkeypatch):
    monkeypatch.setattr(uuid_map, "_agent_map",  {JETT_UUID.lower(): "Jett"})
    monkeypatch.setattr(uuid_map, "_maps_loaded", True)
    assert uuid_map.resolve_agent(JETT_UUID.upper()) == "Jett"


def test_load_maps_network_failure_is_nonfatal(monkeypatch, tmp_path):
    """load_maps() returns empty maps (not an exception) when network fails."""
    monkeypatch.setattr(uuid_map, "AGENTS_CACHE",  tmp_path / "agents.json")
    monkeypatch.setattr(uuid_map, "WEAPONS_CACHE", tmp_path / "weapons.json")
    monkeypatch.setattr(uuid_map, "_maps_loaded", False)

    def _fail():
        raise ConnectionError("network down")

    monkeypatch.setattr(uuid_map, "_fetch_agents",  _fail)
    monkeypatch.setattr(uuid_map, "_fetch_weapons", _fail)

    uuid_map.load_maps()  # must not raise
    assert uuid_map._agent_map  == {}
    assert uuid_map._weapon_map == {}


def test_load_maps_reads_from_fresh_cache(monkeypatch, tmp_path):
    """load_maps() uses disk cache when file is < 24h old."""
    agents_file  = tmp_path / "agents.json"
    weapons_file = tmp_path / "weapons.json"

    agents_file.write_text(json.dumps({JETT_UUID: "Jett", "_ts": time.time()}))
    weapons_file.write_text(json.dumps({VANDAL_UUID: "Vandal", "_ts": time.time()}))

    monkeypatch.setattr(uuid_map, "AGENTS_CACHE",  agents_file)
    monkeypatch.setattr(uuid_map, "WEAPONS_CACHE", weapons_file)
    monkeypatch.setattr(uuid_map, "CACHE_DIR",     tmp_path)
    monkeypatch.setattr(uuid_map, "_maps_loaded",  False)

    fetch_called = {"agents": 0, "weapons": 0}
    monkeypatch.setattr(uuid_map, "_fetch_agents",  lambda: fetch_called.__setitem__("agents",  1) or {})
    monkeypatch.setattr(uuid_map, "_fetch_weapons", lambda: fetch_called.__setitem__("weapons", 1) or {})

    uuid_map.load_maps()
    assert uuid_map._agent_map.get(JETT_UUID)   == "Jett"
    assert uuid_map._weapon_map.get(VANDAL_UUID) == "Vandal"
    assert fetch_called["agents"]  == 0  # not fetched from network
    assert fetch_called["weapons"] == 0


def test_load_maps_refetches_stale_cache(monkeypatch, tmp_path):
    """load_maps() fetches from network when cache is > 24h old."""
    agents_file  = tmp_path / "agents.json"
    weapons_file = tmp_path / "weapons.json"

    stale_ts = time.time() - 100_000  # ~28h ago
    agents_file.write_text(json.dumps({JETT_UUID: "OldJett", "_ts": stale_ts}))
    weapons_file.write_text(json.dumps({VANDAL_UUID: "OldVandal", "_ts": stale_ts}))

    monkeypatch.setattr(uuid_map, "AGENTS_CACHE",  agents_file)
    monkeypatch.setattr(uuid_map, "WEAPONS_CACHE", weapons_file)
    monkeypatch.setattr(uuid_map, "CACHE_DIR",     tmp_path)
    monkeypatch.setattr(uuid_map, "_maps_loaded",  False)
    monkeypatch.setattr(uuid_map, "_fetch_agents",  lambda: {JETT_UUID: "Jett"})
    monkeypatch.setattr(uuid_map, "_fetch_weapons", lambda: {VANDAL_UUID: "Vandal"})

    uuid_map.load_maps()
    assert uuid_map._agent_map.get(JETT_UUID)   == "Jett"     # fresh data
    assert uuid_map._weapon_map.get(VANDAL_UUID) == "Vandal"
