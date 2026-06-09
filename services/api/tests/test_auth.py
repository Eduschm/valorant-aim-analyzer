"""Gate tests for magic link + JWT auth — no Resend, no Riot, all local."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest


def _request_link(client, email="edu@example.com"):
    """DEV_MODE on so the endpoint returns the link without email delivery."""
    with patch.dict(os.environ, {"DEV_MODE": "true"}, clear=False):
        resp = client.post("/api/v1/auth/magic-link", json={"email": email})
    assert resp.status_code == 200
    return resp.json()


def _extract_token(dev_link: str) -> str:
    return dev_link.split("token=")[1]


# ------------------------------------------------------------------ #
# JWT unit tests
# ------------------------------------------------------------------ #

def test_jwt_round_trip():
    from services.api import auth
    token = auth.create_jwt("user-123")
    assert auth.decode_jwt(token) == "user-123"


def test_jwt_garbage_returns_none():
    from services.api import auth
    assert auth.decode_jwt("not.a.jwt") is None
    assert auth.decode_jwt("") is None


# ------------------------------------------------------------------ #
# Magic link request
# ------------------------------------------------------------------ #

def test_magic_link_creates_user_and_returns_dev_link(client):
    data = _request_link(client)
    assert "dev_link" in data
    assert "token=" in data["dev_link"]


def test_magic_link_hides_link_outside_dev_mode(client):
    with patch.dict(os.environ, {"DEV_MODE": "false"}, clear=False):
        resp = client.post("/api/v1/auth/magic-link", json={"email": "x@example.com"})
    assert resp.status_code == 200
    assert "dev_link" not in resp.json()


def test_magic_link_invalid_email_rejected(client):
    resp = client.post("/api/v1/auth/magic-link", json={"email": "not-an-email"})
    assert resp.status_code == 422


def test_magic_link_sends_via_resend_when_key_set(client):
    sent = {}

    def fake_send(to, link):
        sent["to"], sent["link"] = to, link

    with (
        patch.dict(os.environ, {"RESEND_API_KEY": "re_test", "DEV_MODE": "false"}, clear=False),
        patch("services.api.auth._send_email_sync", side_effect=fake_send),
    ):
        resp = client.post("/api/v1/auth/magic-link", json={"email": "mail@example.com"})
    assert resp.status_code == 200
    assert sent["to"] == "mail@example.com"
    assert "token=" in sent["link"]


# ------------------------------------------------------------------ #
# Verify
# ------------------------------------------------------------------ #

def test_verify_valid_token_sets_cookie_and_redirects(client):
    token = _extract_token(_request_link(client)["dev_link"])
    resp = client.get(f"/api/v1/auth/verify?token={token}", follow_redirects=False)
    assert resp.status_code == 307
    assert "auth_token" in resp.cookies


def test_verify_invalid_token_400(client):
    resp = client.get("/api/v1/auth/verify?token=bogus", follow_redirects=False)
    assert resp.status_code == 400


def test_verify_token_single_use(client):
    token = _extract_token(_request_link(client)["dev_link"])
    first = client.get(f"/api/v1/auth/verify?token={token}", follow_redirects=False)
    assert first.status_code == 307
    second = client.get(f"/api/v1/auth/verify?token={token}", follow_redirects=False)
    assert second.status_code == 400
    assert "already used" in second.json()["detail"]


def test_verify_expired_token_400(client):
    import asyncio
    from sqlalchemy import update
    from services.api.database import SessionLocal
    from services.api.models import MagicToken

    token = _extract_token(_request_link(client)["dev_link"])

    async def expire_all():
        async with SessionLocal() as session:
            await session.execute(
                update(MagicToken).values(expires_at=datetime.utcnow() - timedelta(minutes=1))
            )
            await session.commit()

    asyncio.run(expire_all())

    resp = client.get(f"/api/v1/auth/verify?token={token}", follow_redirects=False)
    assert resp.status_code == 400
    assert "expired" in resp.json()["detail"]


# ------------------------------------------------------------------ #
# get_current_user / /me
# ------------------------------------------------------------------ #

def test_me_requires_auth(client):
    resp = client.get("/api/v1/me")
    assert resp.status_code == 401


def test_me_with_cookie(client):
    token = _extract_token(_request_link(client, "me@example.com")["dev_link"])
    client.get(f"/api/v1/auth/verify?token={token}", follow_redirects=False)
    resp = client.get("/api/v1/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "me@example.com"
    assert data["is_paid"] is False
    assert data["credits_used"] == 0


def test_me_with_bearer_header(client):
    from services.api import auth as auth_mod
    data = _request_link(client, "bearer@example.com")
    token = _extract_token(data["dev_link"])
    resp = client.get(f"/api/v1/auth/verify?token={token}", follow_redirects=False)
    jwt_token = resp.cookies["auth_token"]
    client.cookies.clear()
    resp = client.get("/api/v1/me", headers={"Authorization": f"Bearer {jwt_token}"})
    assert resp.status_code == 200
    assert auth_mod.decode_jwt(jwt_token) is not None


# ------------------------------------------------------------------ #
# Riot ID linking
# ------------------------------------------------------------------ #

def _sign_in(client, email="riot@example.com"):
    token = _extract_token(_request_link(client, email)["dev_link"])
    client.get(f"/api/v1/auth/verify?token={token}", follow_redirects=False)


def test_link_riot_id_requires_auth(client):
    resp = client.post("/api/v1/auth/riot-id", json={"riot_id": "Name#TAG"})
    assert resp.status_code == 401


def test_link_riot_id_saves_canonical_id(client, mock_riot_report):
    _sign_in(client)
    with patch("services.riot.service.get_riot_report",
               new=AsyncMock(return_value=mock_riot_report)):
        resp = client.post("/api/v1/auth/riot-id", json={"riot_id": "testplayer#na1"})
    assert resp.status_code == 200
    assert resp.json()["riot_id"] == "TestPlayer#NA1"

    me = client.get("/api/v1/me").json()
    assert me["riot_id"] == "TestPlayer#NA1"


def test_link_riot_id_invalid_player_400(client):
    from services.riot.client import RiotAPIError
    _sign_in(client)
    with patch("services.riot.service.get_riot_report",
               new=AsyncMock(side_effect=RiotAPIError(404, "not found"))):
        resp = client.post("/api/v1/auth/riot-id", json={"riot_id": "Ghost#NOPE"})
    assert resp.status_code == 400
    assert "not found" in resp.json()["detail"].lower()


# ------------------------------------------------------------------ #
# Dev bypass now issues real JWTs against real users
# ------------------------------------------------------------------ #

def test_dev_bypass_token_works_with_me(monkeypatch, client):
    import services.api.main as main_mod
    monkeypatch.setattr(main_mod, "DEV_MODE", True)
    create = client.post("/api/v1/dev/create-account", json={"email": "dev@test.com"})
    assert create.status_code == 200
    token = create.json()["token"]
    client.cookies.clear()
    resp = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "dev@test.com"


def test_dev_bypass_is_idempotent_per_email(monkeypatch, client):
    import services.api.main as main_mod
    monkeypatch.setattr(main_mod, "DEV_MODE", True)
    first = client.post("/api/v1/dev/create-account", json={"email": "same@test.com"})
    second = client.post("/api/v1/dev/create-account", json={"email": "same@test.com"})
    assert first.json()["user"]["id"] == second.json()["user"]["id"]
