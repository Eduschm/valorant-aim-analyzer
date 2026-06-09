"""Gate tests for free tier credit enforcement (Task D) — all mocked."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def signed_in(monkeypatch, client):
    """Dev-bypass account + auth cookie on the client. Returns the user email."""
    import services.api.main as main_mod
    monkeypatch.setattr(main_mod, "DEV_MODE", True)
    resp = client.post("/api/v1/dev/create-account", json={"email": "credits@test.com"})
    assert resp.status_code == 200
    return "credits@test.com"


def _set_user(email: str, **values):
    from sqlalchemy import update
    from services.api.database import SessionLocal
    from services.api.models import User

    async def _apply():
        async with SessionLocal() as session:
            await session.execute(update(User).where(User.email == email).values(**values))
            await session.commit()

    asyncio.run(_apply())


def _analyze(client):
    with (
        patch("services.riot.service.get_riot_report", new=AsyncMock(side_effect=Exception("skip"))),
    ):
        return client.post("/api/v1/analyze", json={"riot_id": "Player#NA1"})


def test_anonymous_analyze_still_works(client):
    resp = _analyze(client)
    assert resp.status_code == 200


def test_authed_analyze_consumes_credit(client, signed_in):
    resp = _analyze(client)
    assert resp.status_code == 200
    assert client.get("/api/v1/me").json()["credits_used"] == 1


def test_authed_report_linked_to_user(client, signed_in):
    resp = _analyze(client)
    report_id = resp.json()["report_id"]

    from sqlalchemy import select
    from services.api.database import SessionLocal
    from services.api.models import Report, User

    async def _fetch():
        async with SessionLocal() as session:
            report = (await session.execute(select(Report).where(Report.id == report_id))).scalar_one()
            user = (await session.execute(select(User).where(User.email == signed_in))).scalar_one()
            return report.user_id, user.id

    report_user_id, user_id = asyncio.run(_fetch())
    assert report_user_id == user_id


def test_free_tier_blocks_when_credits_spent(client, signed_in):
    from services.api.main import FREE_TIER_CREDITS
    _set_user(signed_in, credits_used=FREE_TIER_CREDITS)
    resp = _analyze(client)
    assert resp.status_code == 429
    assert "Free tier limit" in resp.json()["detail"]


def test_paid_user_unlimited(client, signed_in):
    _set_user(signed_in, is_paid=True, credits_used=999)
    resp = _analyze(client)
    assert resp.status_code == 200
    assert client.get("/api/v1/me").json()["credits_used"] == 999  # untouched


def test_credits_reset_after_period(client, signed_in):
    from services.api.main import CREDIT_PERIOD_DAYS, FREE_TIER_CREDITS
    _set_user(
        signed_in,
        credits_used=FREE_TIER_CREDITS,
        credits_reset_at=datetime.utcnow() - timedelta(days=CREDIT_PERIOD_DAYS + 1),
    )
    resp = _analyze(client)
    assert resp.status_code == 200
    assert client.get("/api/v1/me").json()["credits_used"] == 1
