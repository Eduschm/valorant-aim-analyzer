"""
Auth: magic link (Resend) + JWT sessions.

Flow:
  POST /api/v1/auth/magic-link  → create_magic_link(email, db)
      get-or-create User, mint a single-use token (15 min expiry),
      email the link via Resend (or log it when no RESEND_API_KEY).
  GET  /api/v1/auth/verify?token=xxx → verify_token(token, db)
      validate + mark used, return a 7-day JWT for the auth_token cookie.
  Protected routes depend on get_current_user (cookie or Bearer header).

Only the sha256 of the magic token is stored — the raw value exists solely
in the emailed link.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from .database import get_db
    from .models import MagicToken, User
except ImportError:
    from database import get_db  # type: ignore
    from models import MagicToken, User  # type: ignore

from services.logging import get_logger

logger = get_logger("services.api.auth")

MAGIC_TOKEN_TTL_MINUTES = 15
JWT_TTL_DAYS = 7
JWT_ALGORITHM = "HS256"

_jwt_secret = os.getenv("JWT_SECRET")
if not _jwt_secret:
    # Ephemeral secret: sessions die on restart. Fine for dev, set JWT_SECRET in prod.
    _jwt_secret = secrets.token_hex(32)
    logger.warning("JWT_SECRET not set — using ephemeral secret, sessions won't survive restarts")
JWT_SECRET = _jwt_secret


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


# ------------------------------------------------------------------
# JWT
# ------------------------------------------------------------------

def create_jwt(user_id: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(days=JWT_TTL_DAYS)
    return jwt.encode({"sub": user_id, "exp": expires}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> str | None:
    """Return the user_id, or None if the token is invalid/expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# ------------------------------------------------------------------
# Magic link
# ------------------------------------------------------------------

async def get_or_create_user(email: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(email=email)
        db.add(user)
        await db.commit()
        logger.info("Created user %s", email)
    return user


def _build_verify_link(token: str) -> str:
    api_base = os.getenv("API_BASE_URL", "http://localhost:8000")
    return f"{api_base}/api/v1/auth/verify?token={token}"


def _send_email_sync(to: str, link: str) -> None:
    import resend

    resend.api_key = os.environ["RESEND_API_KEY"]
    resend.Emails.send({
        "from": os.getenv("EMAIL_FROM", "onboarding@resend.dev"),
        "to": to,
        "subject": "Your Valorant Aim Analyzer sign-in link",
        "html": (
            f'<p>Click to sign in (expires in {MAGIC_TOKEN_TTL_MINUTES} minutes):</p>'
            f'<p><a href="{link}">Sign in to Valorant Aim Analyzer</a></p>'
            f'<p>If you did not request this, ignore this email.</p>'
        ),
    })


async def create_magic_link(email: str, db: AsyncSession) -> dict:
    """
    Mint a magic token for the email and deliver the link.
    Returns {"sent": bool, "dev_link": str | None} — dev_link only in DEV_MODE
    so local dev works without Resend.
    """
    user = await get_or_create_user(email, db)

    raw_token = secrets.token_urlsafe(32)
    db.add(MagicToken(
        token_hash=_hash_token(raw_token),
        user_id=user.id,
        expires_at=_utcnow() + timedelta(minutes=MAGIC_TOKEN_TTL_MINUTES),
    ))
    await db.commit()

    link = _build_verify_link(raw_token)
    dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"

    if os.getenv("RESEND_API_KEY"):
        # Resend SDK is sync — keep it off the event loop
        await asyncio.to_thread(_send_email_sync, email, link)
        logger.info("Magic link emailed to %s", email)
        return {"sent": True, "dev_link": link if dev_mode else None}

    logger.warning("RESEND_API_KEY not set — magic link for %s: %s", email, link)
    return {"sent": False, "dev_link": link if dev_mode else None}


async def verify_token(token: str, db: AsyncSession) -> tuple[User, str]:
    """
    Validate a magic token: must exist, be unused, and not expired.
    Marks it used and returns (user, jwt). Raises HTTPException(400) otherwise.
    """
    result = await db.execute(
        select(MagicToken).where(MagicToken.token_hash == _hash_token(token))
    )
    record = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(status_code=400, detail="Invalid sign-in link.")
    if record.used_at is not None:
        raise HTTPException(status_code=400, detail="This sign-in link was already used.")
    if record.expires_at < _utcnow():
        raise HTTPException(status_code=400, detail="This sign-in link expired. Request a new one.")

    record.used_at = _utcnow()
    user = await db.get(User, record.user_id)
    await db.commit()

    return user, create_jwt(user.id)


# ------------------------------------------------------------------
# FastAPI dependencies
# ------------------------------------------------------------------

def _extract_token(request: Request) -> str | None:
    token = request.cookies.get("auth_token")
    if token:
        return token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.removeprefix("Bearer ")
    return None


async def get_optional_user(request: Request, db: AsyncSession = Depends(get_db)) -> User | None:
    """Resolve the current user if a valid token is present, else None."""
    token = _extract_token(request)
    if not token:
        return None
    user_id = decode_jwt(token)
    if not user_id:
        return None
    return await db.get(User, user_id)


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """Require auth — 401 when missing/invalid."""
    user = await get_optional_user(request, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return user
