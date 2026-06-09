"""
Database-backed report store — replaces store.InMemoryStore.

Each method opens its own session: background tasks run outside any request
scope, so per-call sessions are the only safe pattern here.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

try:
    from .database import SessionLocal
    from .models import Report
except ImportError:
    from database import SessionLocal  # type: ignore
    from models import Report  # type: ignore


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class DatabaseStore:
    async def create(self, riot_id: str, user_id: str | None = None) -> Report:
        async with SessionLocal() as session:
            report = Report(riot_id=riot_id, user_id=user_id, status="queued")
            session.add(report)
            await session.commit()
            return report

    async def get(self, report_id: str) -> Report | None:
        async with SessionLocal() as session:
            result = await session.execute(select(Report).where(Report.id == report_id))
            return result.scalar_one_or_none()

    async def update(self, report_id: str, **kwargs) -> Report | None:
        async with SessionLocal() as session:
            result = await session.execute(select(Report).where(Report.id == report_id))
            report = result.scalar_one_or_none()
            if report is None:
                return None
            for key, value in kwargs.items():
                setattr(report, key, value)
            if kwargs.get("status") in ("done", "error"):
                report.completed_at = _utcnow()
            await session.commit()
            return report


# Singleton — shared across the FastAPI process
db_store = DatabaseStore()
