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

from fastapi import FastAPI, HTTPException, BackgroundTasks, Response, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from services.logging import configure_logging, get_logger

load_dotenv()
configure_logging()
logger = get_logger("services.api.main")

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

try:
    from .schemas import AnalyzeRequest, AnalyzeResponse, ReportResponse, MagicLinkRequest, LinkRiotIdRequest
    from .db_store import db_store
    from .database import init_db, get_db
    from .models import User
    from . import auth
except ImportError:
    # Fallback for running with: uvicorn main:app (not as package)
    from schemas import AnalyzeRequest, AnalyzeResponse, ReportResponse, MagicLinkRequest, LinkRiotIdRequest  # type: ignore
    from db_store import db_store  # type: ignore
    from database import init_db, get_db  # type: ignore
    from models import User  # type: ignore
    import auth  # type: ignore

AUTH_COOKIE_MAX_AGE = 60 * 60 * 24 * auth.JWT_TTL_DAYS


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=AUTH_COOKIE_MAX_AGE,
    )


def _user_payload(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "riot_id": user.riot_id,
        "is_paid": user.is_paid,
        "credits_used": user.credits_used,
        "created_at": user.created_at.isoformat(),
    }

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creates tables for sqlite dev; production schemas come from alembic.
    await init_db()
    logger.info("Database initialized")
    yield


app = FastAPI(title="Valorant Aim Analyzer API", version="0.1.0", lifespan=lifespan)
logger.info("Starting API app: DEV_MODE=%s", DEV_MODE)

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
    logger.info("Received analysis request for %s region=%s", body.riot_id, body.region)
    record = await db_store.create(body.riot_id)
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
    await db_store.update(report_id, status="processing")
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

        await db_store.update(
            report_id,
            status="done",
            riot_report=dataclasses.asdict(riot),
            coaching=dataclasses.asdict(coaching),
        )
        logger.info("Background task complete report=%s riot_id=%s status=done", report_id, riot_id)
    except Exception as exc:
        logger.exception("Background task failed report=%s riot_id=%s", report_id, riot_id)
        await db_store.update(report_id, status="error", error=_friendly_error(exc))


@app.get("/api/v1/report/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    """Poll for report status + results."""
    record = await db_store.get(report_id)
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
# Auth — magic link + JWT (services/api/auth.py)
# ------------------------------------------------------------------

@app.post("/api/v1/auth/magic-link")
async def request_magic_link(body: MagicLinkRequest, db: AsyncSession = Depends(get_db)):
    """
    Email a single-use sign-in link (15 min expiry).
    Without RESEND_API_KEY the link is logged server-side; in DEV_MODE it is
    also returned as dev_link so local dev works without email.
    """
    result = await auth.create_magic_link(body.email, db)
    response = {"message": "If that email is valid, a sign-in link is on its way."}
    if result["dev_link"]:
        response["dev_link"] = result["dev_link"]
    return response


@app.get("/api/v1/auth/verify")
async def verify_magic_link(token: str, db: AsyncSession = Depends(get_db)):
    """Validate the magic token, set the auth cookie, send the user home."""
    user, jwt_token = await auth.verify_token(token, db)
    logger.info("User %s signed in via magic link", user.email)
    response = RedirectResponse(url=os.getenv("FRONTEND_URL", "http://localhost:3000"))
    _set_auth_cookie(response, jwt_token)
    return response


@app.post("/api/v1/auth/riot-id")
async def link_riot_id(
    body: LinkRiotIdRequest,
    user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Validate the Riot ID against the Riot API and save it to the account."""
    try:
        from services.riot.service import get_riot_report
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from riot.service import get_riot_report  # type: ignore

    try:
        report = await get_riot_report(body.riot_id, match_count=1)
    except Exception as exc:
        logger.warning("Riot ID validation failed for %s: %s", body.riot_id, exc)
        raise HTTPException(status_code=400, detail=_friendly_error(exc))

    user.riot_id = f"{report.game_name}#{report.tag_line}"
    db.add(user)
    await db.commit()
    return {"riot_id": user.riot_id, "message": "Riot ID linked."}


@app.get("/api/v1/me")
async def get_me(user: User = Depends(auth.get_current_user)):
    """Current authenticated user — used by the frontend to hydrate auth state."""
    return _user_payload(user)


# ------------------------------------------------------------------
# Dev bypass — only active when DEV_MODE=true in .env
# NEVER expose these in production
# ------------------------------------------------------------------

class DevCreateAccountRequest(BaseModel):
    email:   str = "dev@localhost"
    riot_id: str | None = None


@app.post("/api/v1/dev/create-account")
async def dev_create_account(
    body: DevCreateAccountRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Create (or reuse) a real DB user and return a real JWT immediately.
    No email, no magic link. Only works when DEV_MODE=true in .env.
    Pass the token as Authorization: Bearer <token>, or rely on the
    auth_token cookie this sets.
    """
    if not DEV_MODE:
        raise HTTPException(status_code=404, detail="Not found")

    user = await auth.get_or_create_user(body.email.strip().lower(), db)
    if body.riot_id:
        user.riot_id = body.riot_id
        db.add(user)
        await db.commit()

    token = auth.create_jwt(user.id)
    _set_auth_cookie(response, token)

    return {
        "token":   token,
        "user":    _user_payload(user),
        "message": "Dev account created. Token set as auth_token cookie.",
    }


@app.get("/api/v1/dev/session")
async def dev_get_session(token: str | None = None, db: AsyncSession = Depends(get_db)):
    """Look up a dev session by JWT. Used to verify the bypass worked."""
    if not DEV_MODE:
        raise HTTPException(status_code=404, detail="Not found")
    user_id = auth.decode_jwt(token) if token else None
    user = await db.get(User, user_id) if user_id else None
    if user is None:
        return {"authenticated": False}
    return {"authenticated": True, "user": _user_payload(user)}
