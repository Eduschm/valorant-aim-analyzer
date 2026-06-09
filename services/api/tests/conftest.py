"""
API test config — points DATABASE_URL at a throwaway sqlite file BEFORE
services.api.database is imported (it reads the env var at import time).
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "valorant_api_test.db")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

import asyncio

import pytest
from fastapi.testclient import TestClient


def _reset_database():
    """Drop + recreate all tables through the app engine.

    Deleting the sqlite file between tests is unsafe: a stale journal file
    from a previous connection can roll back commits made against the
    recreated database. DDL through the same engine has no such problem.
    """
    from services.api.database import Base, engine
    import services.api.models  # noqa: F401 — registers tables

    async def _reset():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_reset())


@pytest.fixture
def client():
    from services.api.main import app, limiter
    _reset_database()
    limiter._storage.reset()
    with TestClient(app) as c:
        yield c
