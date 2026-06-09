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

import uuid
import datetime
import secrets
import hashlib

from fastapi import FastAPI, HTTPException, BackgroundTasks, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from services.logging import configure_logging, get_logger

load_dotenv()
configure_logging()
logger = get_logger("services.api.main")

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

try:
    from .schemas import AnalyzeRequest, AnalyzeResponse, ReportResponse, MagicLinkRequest, LinkRiotIdRequest
    from .store   import store
except ImportError:
    # Fallback for running with: uvicorn main:app (not as package)
    from schemas import AnalyzeRequest, AnalyzeResponse, ReportResponse, MagicLinkRequest, LinkRiotIdRequest  # type: ignore
    from store   import store  # type: ignore

# Simple in-memory session store (replaced by DB+JWT in auth implementation)
# token → user dict
_sessions: dict[str, dict] = {}


def _make_token(user_id: str) -> str:
    raw = f"{user_id}:{secrets.token_hex(32)}"
    return hashlib.sha256(raw.encode()).hexdigest()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Valorant Aim Analyzer API", version="0.1.0")
app.state.limiter = limiter
logger.info("Starting API app: DEV_MODE=%s", DEV_MODE)


from fastapi.responses import JSONResponse


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    retry_after = getattr(exc, "retry_after", 60) or 60
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}. Try again later."},
        headers={"Retry-After": str(retry_after)},
    )

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
@limiter.limit("10/minute")
async def submit_analysis(request: Request, body: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Submit a Riot ID for analysis.
    Runs the riot + LLM pipeline in the background and returns a report_id.
    Poll GET /api/v1/report/{report_id} until status == "done".
    """
    logger.info("Received analysis request for %s region=%s", body.riot_id, body.region)
    record = store.create(body.riot_id)
    background_tasks.add_task(_run_analysis, record.id, body.riot_id, body.region)
    logger.info("Queued background analysis report=%s riot_id=%s region=%s", record.id, body.riot_id, body.region)
    return AnalyzeResponse(report_id=record.id, status="queued")


def _friendly_error(exc: Exception) -> str:
    """Turn a raw pipeline exception into a clear, actionable message for the UI."""
    status = getattr(exc, "status", None)
    is_henrik = type(exc).__name__ == "HenrikAPIError"

    if status == 404:
        return "Player not found. Double-check the Riot ID (Name#TAG) and region, then try again."
    if status == 429:
        provider = "Henrik" if is_henrik else "Riot"
        return f"{provider} API rate limit hit. Wait a minute and try again."

    if is_henrik:
        if status == 401:
            return (
                "Henrik API key is missing. Add HENRIK_API_KEY to .env — get a free key from "
                "the HenrikDev Discord (https://discord.com/invite/X3GaVkX2YN, #get-a-key)."
            )
        if status == 403:
            return (
                "Henrik API key is invalid. Replace HENRIK_API_KEY in .env with a valid key "
                "from the HenrikDev Discord (#get-a-key)."
            )
    else:
        if status == 401:
            return "Riot API key is invalid or expired. Update RIOT_API_KEY in .env (dev keys expire every 24h)."
        if status == 403:
            return (
                "Your Riot API key does not have Valorant access. Personal/dev keys only cover "
                "account lookup. Set HENRIK_API_KEY to use the Henrik provider, or apply for a "
                "production Riot key with the Valorant product at developer.riotgames.com."
            )

    msg = str(exc)
    return msg or "Analysis failed due to an unexpected error."


async def _run_analysis(report_id: str, riot_id: str, region: str = "na"):
    """Background task: fetch Riot data → generate coaching → store result."""
    store.update(report_id, status="processing")
    logger.info("Background task start report=%s riot_id=%s region=%s", report_id, riot_id, region)
    try:
        # Works whether run from repo root (services.riot) or services/api (sys.path set above)
        try:
            from services.riot.service import get_riot_report
            from services.llm.coach    import generate_coaching_report
        except ImportError:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from riot.service import get_riot_report   # type: ignore
            from llm.coach    import generate_coaching_report  # type: ignore

        riot = await get_riot_report(riot_id, region=region)
        coaching = await generate_coaching_report(riot)

        store.update(
            report_id,
            status="done",
            riot_report=dataclasses.asdict(riot),
            coaching=dataclasses.asdict(coaching),
        )
        logger.info("Background task complete report=%s riot_id=%s status=done", report_id, riot_id)
    except Exception as exc:
        logger.exception("Background task failed report=%s riot_id=%s", report_id, riot_id)
        store.update(report_id, status="error", error=_friendly_error(exc))


@app.get("/api/v1/report/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    """Poll for report status + results."""
    record = store.get(report_id)
    if record is None:
        logger.warning("Report not found: %s", report_id)
        raise HTTPException(status_code=404, detail="Report not found")
    logger.debug("Returning report %s status=%s", report_id, record.status)

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


# ------------------------------------------------------------------
# Dev bypass — only active when DEV_MODE=true in .env
# NEVER expose these in production
# ------------------------------------------------------------------

class DevCreateAccountRequest(BaseModel):
    email:   str = "dev@localhost"
    riot_id: str | None = None


@app.post("/api/v1/dev/create-account")
async def dev_create_account(body: DevCreateAccountRequest, response: Response):
    """
    Create a dev account and return a session token immediately.
    No email, no magic link, no database required.

    Only works when DEV_MODE=true in .env.
    Returns a token you can pass as Authorization: Bearer <token>
    or it sets an auth_token cookie automatically.
    """
    if not DEV_MODE:
        raise HTTPException(status_code=404, detail="Not found")

    user_id = str(uuid.uuid4())
    user = {
        "id":       user_id,
        "email":    body.email,
        "riot_id":  body.riot_id,
        "is_paid":  False,
        "created_at": datetime.datetime.utcnow().isoformat(),
    }
    token = _make_token(user_id)
    _sessions[token] = user

    # Set cookie so the frontend picks it up automatically
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )

    return {
        "token":   token,
        "user":    user,
        "message": "Dev account created. Token set as auth_token cookie.",
    }


@app.get("/api/v1/dev/session")
async def dev_get_session(token: str | None = None):
    """Look up a dev session by token. Used to verify the bypass worked."""
    if not DEV_MODE:
        raise HTTPException(status_code=404, detail="Not found")
    if not token or token not in _sessions:
        return {"authenticated": False}
    return {"authenticated": True, "user": _sessions[token]}


@app.delete("/api/v1/dev/sessions")
async def dev_clear_sessions():
    """Clear all dev sessions. Useful for testing."""
    if not DEV_MODE:
        raise HTTPException(status_code=404, detail="Not found")
    _sessions.clear()
    return {"message": "All dev sessions cleared"}
