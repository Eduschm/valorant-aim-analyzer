"""Gate tests for services/riot/uuid_map — no network calls."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import json
import time
import pytest
import services.riot.uuid_map as m


JETT_UUID   = "add6443a-41bd-e414-f6ad-e58d267f4e95"
VANDAL_UUID = "9c82e19d-4575-0200-1a81-3eacf00cf872"


@pytest.fixture(autouse=True)
def inject_test_maps():
    """Give every test a deterministic map with a few known entries."""
    m._agent_map  = {JETT_UUID.lower(): "Jett", "sage-uuid": "Sage"}
    m._weapon_map = {VANDAL_UUID.lower(): "Vandal", "phantom-uuid": "Phantom"}
    m._maps_loaded = True
    yield
    m._agent_map   = {}
    m._weapon_map  = {}
    m._maps_loaded = False


def test_resolve_agent_known_uuid():
    assert m.resolve_agent(JETT_UUID) == "Jett"


def test_resolve_agent_uuid_passthrough_on_miss():
    assert m.resolve_agent("completely-unknown-uuid") == "completely-unknown-uuid"


def test_resolve_weapon_known_uuid():
    assert m.resolve_weapon(VANDAL_UUID) == "Vandal"


def test_resolve_weapon_passthrough_on_miss():
    assert m.resolve_weapon("pistol-uuid") == "pistol-uuid"


def test_resolve_agent_case_insensitive():
    assert m.resolve_agent(JETT_UUID.upper()) == "Jett"


def test_load_from_cache_returns_none_for_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "_CACHE_DIR", str(tmp_path))
    result = m._load_from_cache("nonexistent")
    assert result is None


def test_load_from_cache_returns_none_for_stale_file(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "_CACHE_DIR", str(tmp_path))
    path = tmp_path / "agents.json"
    path.write_text(json.dumps({"a": "b"}))
    # Make the file appear 25 hours old
    old_time = time.time() - 90_000
    os.utime(str(path), (old_time, old_time))
    assert m._load_from_cache("agents") is None


def test_load_from_cache_returns_data_for_fresh_file(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "_CACHE_DIR", str(tmp_path))
    expected = {"jett-uuid": "Jett"}
    path = tmp_path / "agents.json"
    path.write_text(json.dumps(expected))
    assert m._load_from_cache("agents") == expected
