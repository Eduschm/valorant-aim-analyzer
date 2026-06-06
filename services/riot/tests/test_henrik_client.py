"""Tests for HenrikClient — all HTTP calls mocked, no real API calls."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from services.riot.henrik_client import HenrikClient, HenrikAPIError


def _mock_response(status: int, json_data: dict) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status
    resp.json.return_value = json_data
    resp.text = str(json_data)
    return resp


# ------------------------------------------------------------------ #
# get_account
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_get_account_unwraps_data():
    resp = _mock_response(200, {"status": 200, "data": {"puuid": "p-1", "name": "TenZ", "tag": "0505"}})
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with HenrikClient("na") as client:
            acct = await client.get_account("TenZ", "0505")
    assert acct["puuid"] == "p-1"


@pytest.mark.asyncio
async def test_get_account_404_raises():
    resp = _mock_response(404, {"status": 404, "errors": [{"message": "not found"}]})
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with HenrikClient("na") as client:
            with pytest.raises(HenrikAPIError) as exc:
                await client.get_account("Ghost", "0000")
    assert exc.value.status == 404


@pytest.mark.asyncio
async def test_missing_key_401_raises():
    resp = _mock_response(401, {"status": 401})
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with HenrikClient("na") as client:
            with pytest.raises(HenrikAPIError) as exc:
                await client.get_matches("TenZ", "0505")
    assert exc.value.status == 401


@pytest.mark.asyncio
async def test_rate_limit_429_raises():
    resp = _mock_response(429, {})
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with HenrikClient("na") as client:
            with pytest.raises(HenrikAPIError) as exc:
                await client.get_mmr("TenZ", "0505")
    assert exc.value.status == 429


# ------------------------------------------------------------------ #
# get_matches / get_mmr unwrap the data envelope
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
async def test_get_matches_returns_list():
    resp = _mock_response(200, {"status": 200, "data": [{"metadata": {"match_id": "m1"}}]})
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with HenrikClient("eu") as client:
            matches = await client.get_matches("TenZ", "0505", size=5)
    assert isinstance(matches, list)
    assert matches[0]["metadata"]["match_id"] == "m1"


@pytest.mark.asyncio
async def test_get_mmr_returns_data():
    resp = _mock_response(200, {"status": 200, "data": {"current": {"tier": {"id": 13, "name": "Gold 2"}}}})
    with patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=resp)):
        async with HenrikClient("na") as client:
            mmr = await client.get_mmr("TenZ", "0505")
    assert mmr["current"]["tier"]["name"] == "Gold 2"


# ------------------------------------------------------------------ #
# Affinity normalization
# ------------------------------------------------------------------ #

def test_affinity_valid_passthrough():
    assert HenrikClient("eu").affinity == "eu"
    assert HenrikClient("KR").affinity == "kr"


def test_affinity_invalid_defaults_na():
    assert HenrikClient("mars").affinity == "na"


@pytest.mark.asyncio
async def test_async_context_manager_closes_client():
    async with HenrikClient("na") as client:
        assert client._client is not None
    assert client._client.is_closed
