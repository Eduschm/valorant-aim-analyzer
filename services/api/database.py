"""
Async SQLAlchemy engine + session factory.

DATABASE_URL examples:
  postgresql://user:pass@host/db       (auto-normalized to postgresql+asyncpg://)
  sqlite+aiosqlite:///./valorant.db    (default — zero-config local dev)

Production uses alembic migrations (services/api/alembic). Local sqlite dev
creates tables automatically on startup via init_db().
"""

from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

DEFAULT_SQLITE_URL = "sqlite+aiosqlite:///./valorant.db"


def _normalize_url(url: str) -> str:
    """Map sync driver URLs (what Neon/Supabase hand out) to async drivers."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return url


DATABASE_URL = _normalize_url(os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL))


class Base(DeclarativeBase):
    pass


def _engine_kwargs(url: str) -> dict:
    # sqlite connections carry event-loop affinity; NullPool prevents a pooled
    # connection created on one loop from being reused on another (TestClient
    # and background tasks each run their own loop).
    if url.startswith("sqlite"):
        return {"poolclass": NullPool}
    return {"pool_pre_ping": True}


engine = create_async_engine(DATABASE_URL, **_engine_kwargs(DATABASE_URL))
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Create all tables. Used for sqlite dev + tests; prod runs alembic."""
    # Import registers the ORM tables on Base.metadata
    try:
        from . import models  # noqa: F401
    except ImportError:
        import models  # type: ignore  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """FastAPI dependency — yields one AsyncSession per request."""
    async with SessionLocal() as session:
        yield session
