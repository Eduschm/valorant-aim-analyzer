"""
In-memory report store for MVP.
Replace with PostgreSQL (see AGENT_TASKS.md Step 1) when ready to persist data.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ReportRecord:
    id:           str
    riot_id:      str
    status:       str               # queued | processing | done | error
    riot_report:  dict | None = None
    cv_report:    dict | None = None
    coaching:     dict | None = None
    error:        str | None = None
    created_at:   datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class InMemoryStore:
    def __init__(self):
        self._reports: dict[str, ReportRecord] = {}

    def create(self, riot_id: str) -> ReportRecord:
        record = ReportRecord(id=str(uuid.uuid4()), riot_id=riot_id, status="queued")
        self._reports[record.id] = record
        return record

    def get(self, report_id: str) -> ReportRecord | None:
        return self._reports.get(report_id)

    def update(self, report_id: str, **kwargs) -> ReportRecord | None:
        record = self._reports.get(report_id)
        if record is None:
            return None
        for k, v in kwargs.items():
            setattr(record, k, v)
        if kwargs.get("status") in ("done", "error"):
            record.completed_at = datetime.utcnow()
        return record


# Singleton — shared across the FastAPI process
store = InMemoryStore()
