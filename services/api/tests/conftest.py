"""
Auto-reset the rate limiter storage between every API test.
Without this, rate_limit tests that exhaust the 10/min bucket
will cause subsequent tests in test_api.py to receive spurious 429s.
"""
import pytest


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    from services.api.main import limiter
    limiter._limiter.storage.reset()
    yield
    limiter._limiter.storage.reset()
