"""Tests for RiotClient — all HTTP calls mocked, no real API calls."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from services.riot.client import RiotClient, RiotAPIError


def _mock_response(status: int, json_data: dict) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status
    resp.json.return_value = json_data
    resp.text = str(json_data)
    return resp


# ------------------------------------------------------------------ #
# get_puuid
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_get_puuid_success():
    resp = _mock_response(200, {"puuid": "abc-123", "gameName": "TenZ", "tagLine": "NA1"})
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with RiotClient("na") as client:
            puuid = await client.get_puuid("TenZ", "NA1")
    assert puuid == "abc-123"


@pytest.mark.asyncio
async def test_get_puuid_404_raises():
    resp = _mock_response(404, {"status": {"message": "Not found"}})
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with RiotClient("na") as client:
            with pytest.raises(RiotAPIError) as exc:
                await client.get_puuid("Ghost", "NA1")
    assert exc.value.status == 404


@pytest.mark.asyncio
async def test_get_puuid_429_rate_limit_raises():
    resp = _mock_response(429, {})
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with RiotClient("na") as client:
            with pytest.raises(RiotAPIError) as exc:
                await client.get_puuid("Ghost", "NA1")
    assert exc.value.status == 429


# ------------------------------------------------------------------ #
# get_match_ids
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_get_match_ids_returns_list():
    history = {"history": [{"matchId": f"m{i}"} for i in range(30)]}
    resp = _mock_response(200, history)
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with RiotClient("na") as client:
            ids = await client.get_match_ids("abc-puuid", count=20)
    assert len(ids) == 20
    assert ids[0] == "m0"


@pytest.mark.asyncio
async def test_get_match_ids_fewer_than_count():
    history = {"history": [{"matchId": "m0"}, {"matchId": "m1"}]}
    resp = _mock_response(200, history)
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with RiotClient("na") as client:
            ids = await client.get_match_ids("abc", count=20)
    assert ids == ["m0", "m1"]


# ------------------------------------------------------------------ #
# get_match
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_get_match_returns_dict():
    match_data = {"matchInfo": {"matchId": "xyz"}, "players": [], "teams": []}
    resp = _mock_response(200, match_data)
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with RiotClient("na") as client:
            result = await client.get_match("xyz")
    assert result["matchInfo"]["matchId"] == "xyz"


# ------------------------------------------------------------------ #
# get_rank (Henrik — non-fatal)
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_get_rank_success():
    rank_data = {"data": {"current_data": {"currenttierpatched": "Gold 2", "mmr_change_to_last_game": 15}}}
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 200
    resp.json.return_value = rank_data
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with RiotClient("na") as client:
            result = await client.get_rank("TestPlayer", "NA1")
    assert result == rank_data


@pytest.mark.asyncio
async def test_get_rank_non_fatal_on_500():
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 500
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with RiotClient("na") as client:
            result = await client.get_rank("TestPlayer", "NA1")
    assert result == {}


@pytest.mark.asyncio
async def test_get_rank_non_fatal_on_transport_error():
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(side_effect=httpx.TransportError("conn"))):
        async with RiotClient("na") as client:
            result = await client.get_rank("TestPlayer", "NA1")
    assert result == {}


# ------------------------------------------------------------------ #
# Region routing
# ------------------------------------------------------------------ #

def test_region_routing_eu():
    c = RiotClient("eu")
    assert c.routing == "europe"
    assert c.match_host == "eu.api.riotgames.com"


def test_region_routing_br():
    c = RiotClient("br")
    assert c.routing == "americas"
    assert c.match_host == "br.api.riotgames.com"


def test_region_routing_default():
    c = RiotClient("na")
    assert c.routing == "americas"


# ------------------------------------------------------------------ #
# Async context manager
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_async_context_manager_closes_client():
    async with RiotClient("na") as client:
        assert client._client is not None
    # after exit, close() was called — httpx.AsyncClient is closed
    assert client._client.is_closed
