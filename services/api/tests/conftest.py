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

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Fresh sqlite DB per test — lifespan (init_db) recreates the tables
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    from services.api.main import app, limiter
    limiter._storage.reset()
    with TestClient(app) as c:
        yield c
