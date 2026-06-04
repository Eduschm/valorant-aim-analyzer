# API Service

Core REST API for the Valorant Aim Analyzer. Orchestrates the Riot, LLM, and CV services.

## Quick Start

```bash
cd services/api
python -m uvicorn main:app --reload --port 8000
```

Or from repo root:
```bash
.\dev.ps1  # PowerShell
```

## Architecture

- **Entry point**: `main.py` — FastAPI application
- **In-memory store**: `store.py` — temporary analysis results (replaced by DB in Phase 2)
- **Contracts**: `schemas.py` — request/response types
- **Tests**: `tests/` — pytest suite

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/analyze` | Submit Riot ID for analysis |
| `GET` | `/api/v1/report/{id}` | Poll for report status |
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/auth/dev/create-account` | Dev mode: create test token |
| `GET` | `/auth/dev/session/{token}` | Dev mode: verify token |

## Configuration

Via `.env`:
- `RIOT_API_KEY` — Riot API key (required)
- `ANTHROPIC_API_KEY` — Claude API key (required)
- `DEV_MODE` — Enable dev endpoints (default: false)
- `LOG_LEVEL` — Logging level (default: INFO)

## Dependencies

- FastAPI — HTTP framework
- Uvicorn — ASGI server
- Pydantic — request/response validation
- httpx — async HTTP client for background tasks
- python-dotenv — environment config

## Testing

```bash
python -m pytest services/api/tests/ -v
```

All tests are in `tests/` and use the TestClient fixture from FastAPI.

## Service Dependencies

- **riot**: Fetches Valorant player stats
- **llm**: Generates coaching reports
- **cv** (optional): Video analysis (Phase 2)
