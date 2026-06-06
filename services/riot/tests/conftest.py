"""
Riot service test fixtures.

The uuid_map module fetches from valorant-api.com on first use. This conftest
prevents all gate tests from hitting the network by locking the maps as loaded
(empty → UUID passthrough). Tests that need specific name resolution inject
their own map entries via monkeypatch or direct assignment.
"""
import pytest
import services.riot.uuid_map as uuid_mod


@pytest.fixture(autouse=True)
def lock_uuid_maps():
    """Prevent network fetches in all riot gate tests."""
    orig_agent  = uuid_mod._agent_map.copy()
    orig_weapon = uuid_mod._weapon_map.copy()
    orig_loaded = uuid_mod._maps_loaded
    uuid_mod._maps_loaded = True  # skip _ensure_loaded network call
    yield
    uuid_mod._agent_map  = orig_agent
    uuid_mod._weapon_map = orig_weapon
    uuid_mod._maps_loaded = orig_loaded
