---
name: run-valorant-aim-analyzer
description: Run, start, build, test, screenshot, or smoke-test the valorant-aim-analyzer app. Use when asked to launch the backend API, start the frontend, verify the app works, or run end-to-end smoke tests.
---

Valorant Aim Analyzer: FastAPI backend on :8000 + Next.js 14 frontend on :3000. The agent path is `smoke.sh` (curl-style via Python urllib) for the API and `urllib.request` probes for frontend routes. No Chromium needed for smoke — all pages return server-rendered HTML at 200.

## Prerequisites

- Python venv at `.venv/` with `pip install -r requirements.txt`
- Node 18+ with `cd frontend && npm install`
- `.env` with at minimum `DEV_MODE=true` (dummy values for other keys work for local smoke)

No extra system packages required beyond what's in requirements.txt and package.json.

## Build

```bash
# Python deps (one-time)
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # Windows
# .venv/bin/pip install -r requirements.txt     # Linux/Mac

# Node deps (one-time)
cd frontend && npm install && cd ..
```

## Run (agent path)

The primary driver is `smoke.sh`. It starts both servers, runs all API checks and frontend route probes, then stops them.

```bash
bash .claude/skills/run-valorant-aim-analyzer/smoke.sh
```

Expected output (all 12 lines say `PASS`):

```
  PASS  GET /health  ->  {'status': 'ok', 'version': '0.1.0'}
  PASS  POST /api/v1/dev/create-account  ->  token=...
  PASS  POST /api/v1/analyze  ->  report_id=...
  PASS  GET /api/v1/report/{id}  ->  status=error  (error expected without real RIOT_API_KEY)
  PASS  POST /api/v1/auth/magic-link  ->  501 (not implemented, expected)
  PASS  /  ->  200
  PASS  /analysis/new  ->  200
  PASS  /auth/signin  ->  200
  PASS  /dashboard  ->  200
  PASS  /profile  ->  200
  PASS  /tracker  ->  200
  PASS  /settings  ->  200
```

To hit the API manually while servers are running:

```python
import urllib.request, json

def post(path, body):
    req = urllib.request.Request(
        "http://localhost:8000" + path,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

# Create dev session
status, body = post("/api/v1/dev/create-account", {"email": "dev@localhost"})
token = body["token"]

# Submit analysis
status, body = post("/api/v1/analyze", {"riot_id": "PlayerName#NA1"})
report_id = body["report_id"]
```

## Run (human path)

Two terminals:

```powershell
# Terminal 1 — backend
.\dev.ps1
# → http://localhost:8000

# Terminal 2 — frontend (mock mode, no API keys needed)
.\dev-frontend.ps1
# → http://localhost:3000
```

Set `NEXT_PUBLIC_MOCK_MODE=false` in `frontend/.env.local` to use the real API.

## Frontend QA (visual)

For visually verifying frontend changes (labels, layout, rendering) without a backend or API keys:

```bash
printf 'NEXT_PUBLIC_MOCK_MODE=true\n' > frontend/.env.local
rm -rf frontend/.next
cd frontend && npm run dev   # http://localhost:3000
```

There are **8** pages to QA (the smoke script probes 7 and omits the report page):

| Page | Route to load in mock mode |
| --- | --- |
| Landing | `/` |
| New analysis | `/analysis/new` |
| Report | `/analysis/mock-001` (any id works; `mock-001` is wired in mock data) |
| Tracker | `/tracker` |
| Dashboard | `/dashboard` |
| Profile | `/profile` |
| Settings | `/settings` |
| Sign in | `/auth/signin` |

- Mock data lives in `frontend/lib/mock/analysis.ts` (`MOCK_REPORT`). In mock mode the **report** (`/analysis/mock-001`) and **tracker** (`/tracker`) pages render from it: `current_rank="Gold 2"`, `rank_delta=15`. Good fixtures for verifying rank/label changes — e.g. the rank-delta label renders as `+15 tiers` (the label text is set in `frontend/app/analysis/[id]/page.tsx` and `frontend/app/tracker/page.tsx`).
- `components/auth/AuthGuard.tsx` is **defined but not imported anywhere**, so no page is auth-gated — every route loads directly in the browser without signing in. (May change if auth gets wired up later.)
- To confirm routes respond before opening a browser: `for p in / /analysis/new /analysis/mock-001 /tracker /profile /dashboard /settings /auth/signin; do curl -s -o /dev/null -w "%{http_code}  $p\n" "http://localhost:3000$p"; done`

## Testing

```bash
# Backend (all services, skip CV detector which needs ultralytics)
python -m pytest services/ -v --ignore=services/cv/tests/test_detector.py

# Frontend
cd frontend && npm test
```

- **Known/possibly-preexisting frontend test failure:** `frontend/app/analysis/[id]/__tests__/page.test.tsx` may fail to parse with a RolldownError (`Parse failed`) — the other suites pass (e.g. 22/22). This has reproduced on `main`, so if you see it, check the base branch before assuming your change caused it.

## Gotchas

- **`smoke.sh` exits on subshell syntax error on bash 3.x.** The `( cmd ) &` pattern fails. Use `cmd & PID=$!` instead — that's what `smoke.sh` does.
- **`analysis` endpoint always errors without a real `RIOT_API_KEY`.** `status=error` from `/api/v1/report/{id}` is the correct response when the key is `dummy`. Smoke treats this as a PASS. Rank is derived from the Riot `competitiveTier` field on matches (no Henrik API), so live rank verification needs a real key tied to a Riot account.
- **`/api/v1/auth/magic-link` returns 501** — auth is not implemented yet. Smoke asserts 501 as the expected code.
- **Frontend in mock mode** (`NEXT_PUBLIC_MOCK_MODE=true`) serves all pages with fake data regardless of whether the backend is up. All 8 routes return 200 in mock mode.
- **Python venv path is OS-dependent.** `smoke.sh` tries `.venv/Scripts/python.exe` (Windows) then falls back to `python3` (Linux/Mac).
- **`DEV_MODE=true` required** for `POST /api/v1/dev/create-account`. Without it the endpoint returns 404.
- **Frontend takes ~5s to compile on first request.** The wait loop in `smoke.sh` retries up to 30s.
- **`.next/` cache can serve stale pages.** Delete it before a fresh smoke: `rm -rf frontend/.next`.

## Troubleshooting

**`ModuleNotFoundError: No module named 'fastapi'`** → venv not activated or `pip install -r requirements.txt` not run.

**`ENOENT: next`** → `cd frontend && npm install` not run.

**Port already in use** → kill the existing process. On Linux: `fuser -k 8000/tcp 3000/tcp`. On Windows: `netstat -ano | findstr :8000` then `taskkill /PID <pid> /F`.

**Frontend shows `DemoPlayer#NA1`** → `NEXT_PUBLIC_MOCK_MODE` is `true`. Set to `false` in `frontend/.env.local` and restart.
