"""Gate tests for the database layer — sqlite file, no external services."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


@pytest.fixture(autouse=True)
async def fresh_db():
    from services.api.database import Base, engine
    import services.api.models  # noqa: F401 — registers tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


async def test_create_and_fetch_user():
    from services.api.database import SessionLocal
    from services.api.models import User

    async with SessionLocal() as session:
        user = User(email="edu@example.com")
        session.add(user)
        await session.commit()
        user_id = user.id

    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.email == "edu@example.com"))
        fetched = result.scalar_one()
        assert fetched.id == user_id
        assert fetched.is_paid is False
        assert fetched.credits_used == 0
        assert fetched.riot_id is None


async def test_user_email_unique():
    from services.api.database import SessionLocal
    from services.api.models import User

    async with SessionLocal() as session:
        session.add(User(email="dup@example.com"))
        await session.commit()

    async with SessionLocal() as session:
        session.add(User(email="dup@example.com"))
        with pytest.raises(IntegrityError):
            await session.commit()


async def test_magic_token_belongs_to_user():
    from datetime import datetime, timedelta
    from services.api.database import SessionLocal
    from services.api.models import MagicToken, User

    async with SessionLocal() as session:
        user = User(email="token@example.com")
        session.add(user)
        await session.flush()
        token = MagicToken(
            token_hash="a" * 64,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(minutes=15),
        )
        session.add(token)
        await session.commit()

    async with SessionLocal() as session:
        result = await session.execute(select(MagicToken).where(MagicToken.token_hash == "a" * 64))
        fetched = result.scalar_one()
        assert fetched.used_at is None
        assert fetched.expires_at > datetime.utcnow()


async def test_db_store_create_get_update():
    from services.api.db_store import db_store

    record = await db_store.create("Player#NA1")
    assert record.status == "queued"
    assert record.riot_id == "Player#NA1"
    assert record.user_id is None

    fetched = await db_store.get(record.id)
    assert fetched is not None
    assert fetched.id == record.id

    updated = await db_store.update(record.id, status="processing")
    assert updated.status == "processing"
    assert updated.completed_at is None


async def test_db_store_done_sets_completed_at():
    from services.api.db_store import db_store

    record = await db_store.create("Player#NA1")
    updated = await db_store.update(
        record.id,
        status="done",
        riot_report={"avg_adr": 150.0},
        coaching={"summary": "good"},
    )
    assert updated.status == "done"
    assert updated.completed_at is not None
    assert updated.riot_report == {"avg_adr": 150.0}
    assert updated.coaching == {"summary": "good"}


async def test_db_store_update_missing_returns_none():
    from services.api.db_store import db_store

    assert await db_store.update("no-such-id", status="done") is None
    assert await db_store.get("no-such-id") is None
