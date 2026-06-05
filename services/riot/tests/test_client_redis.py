"""Gate tests for Redis match caching in RiotClient — no real Redis or Riot API."""

from __future__ import annotations

import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.riot.client import RiotClient

MATCH_ID = "test-match-001"
FIXTURE_MATCH = {
    "matchInfo": {"matchId": MATCH_ID, "numberOfRounds": 20},
    "players": [],
    "teams": [],
    "roundResults": [],
}


@pytest.mark.asyncio
async def test_get_match_skips_http_on_cache_hit():
    """Second call for same match ID does not hit the HTTP client."""
    mock_redis = AsyncMock()
    # First call: cache miss. Second call: cache hit.
    mock_redis.get = AsyncMock(side_effect=[None, json.dumps(FIXTURE_MATCH).encode()])
    mock_redis.setex = AsyncMock()

    client = RiotClient("na", redis_client=mock_redis)
    with patch.object(client, "_get", AsyncMock(return_value=FIXTURE_MATCH)) as mock_get:
        result1 = await client.get_match(MATCH_ID)
        result2 = await client.get_match(MATCH_ID)

    # HTTP client called only once — second hit comes from Redis
    assert mock_get.call_count == 1
    assert result1 == FIXTURE_MATCH
    assert result2 == FIXTURE_MATCH


@pytest.mark.asyncio
async def test_get_match_caches_result_after_fetch():
    """After a cache miss, setex is called with the match data."""
    mock_redis = AsyncMock()
    mock_redis.get   = AsyncMock(return_value=None)
    mock_redis.setex = AsyncMock()

    client = RiotClient("na", redis_client=mock_redis)
    with patch.object(client, "_get", AsyncMock(return_value=FIXTURE_MATCH)):
        await client.get_match(MATCH_ID)

    mock_redis.setex.assert_called_once()
    call_args = mock_redis.setex.call_args
    key, ttl, payload = call_args[0]
    assert key == f"match:{MATCH_ID}"
    assert ttl == 86400  # 24h
    assert json.loads(payload) == FIXTURE_MATCH


@pytest.mark.asyncio
async def test_get_match_works_without_redis():
    """No redis_client → match is fetched directly without caching."""
    client = RiotClient("na", redis_client=None)
    with patch.object(client, "_get", AsyncMock(return_value=FIXTURE_MATCH)) as mock_get:
        result = await client.get_match(MATCH_ID)
        result = await client.get_match(MATCH_ID)

    # Both calls hit the HTTP client (no caching)
    assert mock_get.call_count == 2
    assert result == FIXTURE_MATCH


@pytest.mark.asyncio
async def test_get_match_redis_failure_is_nonfatal():
    """Redis errors don't break the match fetch — falls back to HTTP."""
    mock_redis = AsyncMock()
    mock_redis.get   = AsyncMock(side_effect=ConnectionError("Redis down"))
    mock_redis.setex = AsyncMock(side_effect=ConnectionError("Redis down"))

    client = RiotClient("na", redis_client=mock_redis)
    with patch.object(client, "_get", AsyncMock(return_value=FIXTURE_MATCH)):
        result = await client.get_match(MATCH_ID)  # must not raise

    assert result == FIXTURE_MATCH
