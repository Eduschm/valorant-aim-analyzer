"""
API test config — points DATABASE_URL at a throwaway sqlite file BEFORE
services.api.database is imported (it reads the env var at import time).
"""

import os
import tempfile

TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "valorant_api_test.db")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
