"""Pydantic request/response models for the FastAPI routes."""

from __future__ import annotations
from pydantic import BaseModel, field_validator
import re


class AnalyzeRequest(BaseModel):
    riot_id: str

    @field_validator("riot_id")
    @classmethod
    def validate_riot_id(cls, v: str) -> str:
        if not re.match(r"^.+#.+$", v.strip()):
            raise ValueError("riot_id must be in 'Name#TAG' format (e.g. Shroud#1234)")
        return v.strip()


class AnalyzeResponse(BaseModel):
    report_id: str
    status: str       # queued | processing | done | error


class ReportResponse(BaseModel):
    report_id:   str
    status:      str
    riot_report: dict | None = None
    cv_report:   dict | None = None
    coaching:    dict | None = None
    error:       str | None = None


class MagicLinkRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email address")
        return v.strip().lower()


class LinkRiotIdRequest(BaseModel):
    riot_id: str

    @field_validator("riot_id")
    @classmethod
    def validate_riot_id(cls, v: str) -> str:
        if not re.match(r"^.+#.+$", v.strip()):
            raise ValueError("riot_id must be in 'Name#TAG' format")
        return v.strip()
