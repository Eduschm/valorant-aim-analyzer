"""
FastAPI backend — main entrypoint.

Run:
  cd services/api
  uvicorn main:app --reload --port 8000

Auth endpoints are stubbed — see AGENT_TASKS.md Step 2+3 for implementation.
"""

from __future__ import annotations

import dataclasses
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .schemas import AnalyzeRequest, AnalyzeResponse, ReportResponse, MagicLinkRequest, LinkRiotIdRequest
from .store   import store

app = FastAPI(title="Valorant Aim Analyzer API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", "https://yourdomain.com"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# Health
# ------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


# ------------------------------------------------------------------
# Analysis
# ------------------------------------------------------------------

@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def submit_analysis(body: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Submit a Riot ID for analysis.
    Runs the riot + LLM pipeline in the background and returns a report_id.
    Poll GET /api/v1/report/{report_id} until status == "done".
    """
    record = store.create(body.riot_id)
    background_tasks.add_task(_run_analysis, record.id, body.riot_id)
    return AnalyzeResponse(report_id=record.id, status="queued")


async def _run_analysis(report_id: str, riot_id: str):
    """Background task: fetch Riot data → generate coaching → store result."""
    store.update(report_id, status="processing")
    try:
        from services.riot.service import get_riot_report
        from services.llm.coach    import generate_coaching_report

        riot = await get_riot_report(riot_id)
        coaching = await generate_coaching_report(riot)

        store.update(
            report_id,
            status="done",
            riot_report=dataclasses.asdict(riot),
            coaching=dataclasses.asdict(coaching),
        )
    except Exception as exc:
        store.update(report_id, status="error", error=str(exc))


@app.get("/api/v1/report/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    """Poll for report status + results."""
    record = store.get(report_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportResponse(
        report_id=record.id,
        status=record.status,
        riot_report=record.riot_report,
        cv_report=record.cv_report,
        coaching=record.coaching,
        error=record.error,
    )


# ------------------------------------------------------------------
# Auth (stubbed — needs DB + Resend — see AGENT_TASKS.md)
# ------------------------------------------------------------------

@app.post("/api/v1/auth/magic-link")
async def request_magic_link(body: MagicLinkRequest):
    """
    NOT YET IMPLEMENTED.
    Requires: DATABASE_URL (Neon/Supabase), RESEND_API_KEY, JWT_SECRET.
    See services/api/AGENT_TASKS.md Steps 1-3.
    """
    raise HTTPException(
        status_code=501,
        detail="Auth not yet implemented. See services/api/AGENT_TASKS.md.",
    )


@app.get("/api/v1/auth/verify")
async def verify_magic_link(token: str):
    raise HTTPException(status_code=501, detail="Auth not yet implemented.")


@app.post("/api/v1/auth/riot-id")
async def link_riot_id(body: LinkRiotIdRequest):
    raise HTTPException(status_code=501, detail="Auth not yet implemented.")
