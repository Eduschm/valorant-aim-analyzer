# AimLab VAL — Valorant Aim Analyzer

AI-powered aim analysis for Valorant. Paste a Riot ID, get a coaching report in under 30 seconds.

---

## What it does

1. Pulls the last 20 ranked matches from the Riot API
2. Extracts headshot %, ADR, win rate, top agent/weapon, rank delta
3. Feeds stats to Claude Haiku → personalised, number-specific coaching report
4. *(Phase 2)* Runs YOLO on uploaded clips → detects overshoot, undershoot, body-not-head, spray control failures

---

## Project structure

```
valorant-aim-analyzer/
├── contracts/schemas.py          shared typed contracts — all services import from here
├── services/
│   ├── cv/                       YOLO video analysis (standalone)
│   ├── riot/                     Riot API client + match parser
│   ├── llm/                      Claude coaching report generator
│   └── api/                      FastAPI backend — routes, job dispatch, auth stubs
├── frontend/                     Next.js 14 app (App Router)
│   ├── app/                      pages: /, /analysis/new, /analysis/[id], /tracker, /profile, /settings, /dashboard
│   ├── components/               analysis, auth, dashboard, layout, tracker components
│   └── lib/                      api.ts, storage.ts, mock fixtures, types
├── scripts/                      train.py, label_tool.py, Colab training notebook
├── data/                         training dataset (gitignored)
├── AGENTS.md                     full agent handoff — read before building anything
└── .env                          fill in keys (see Keys section)
```

---

## Running locally

### 1. Install dependencies

```powershell
# Root (all services)
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Set up environment

```powershell
# Copy example and fill in at minimum RIOT_API_KEY + ANTHROPIC_API_KEY
copy .env .env        # already exists — edit it directly
```

Minimum required keys:
```
RIOT_API_KEY=RGAPI-...          # from developer.riotgames.com
ANTHROPIC_API_KEY=sk-ant-...    # from console.anthropic.com
DEV_MODE=true                   # enables account bypass
```

### 3. Start backend

```powershell
cd services\api
python -m uvicorn main:app --reload --port 8000
```

API runs at `http://localhost:8000`. Check `http://localhost:8000/health` to confirm.

### 4. Start frontend

```powershell
cd frontend
$env:PATH += ";C:\Program Files\nodejs"    # Windows — only needed if npm not on PATH
npm run dev
```

Frontend runs at `http://localhost:3000`.

### 5. Switch off mock mode

`frontend/.env.local` controls whether the frontend uses real API or fixture data:

```
NEXT_PUBLIC_MOCK_MODE=false     # hit real backend
NEXT_PUBLIC_MOCK_MODE=true      # use fixture data (no backend needed)
```

---

## Pages

| URL | What it shows |
|---|---|
| `/` | Landing page |
| `/analysis/new` | Riot ID input form with autocomplete + region selector |
| `/analysis/[id]` | Report: stats, coaching tips, match history |
| `/tracker` | Rank history chart, HS%/ADR trends, sortable match log |
| `/profile` | Identity, progress since first analysis, usage/credits |
| `/dashboard` | Analysis history table, quick stats |
| `/settings` | Link Riot ID, plan info, dev bypass, sign out |
| `/auth/signin` | Magic link email OR dev bypass button |

---

## Dev account bypass

No email or database needed for local development.

**Option A — UI:** Go to `/auth/signin` → click "Skip auth → go straight to analysis"

**Option B — curl:**
```bash
curl -X POST http://localhost:8000/api/v1/dev/create-account \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@localhost"}'
```

Requires `DEV_MODE=true` in `.env`. Returns a token and sets `auth_token` cookie.

---

## API endpoints

| Method | Path | What it does |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/analyze` | Submit `{"riot_id": "Name#TAG"}` → returns `report_id` |
| `GET` | `/api/v1/report/{id}` | Poll for report status + results |
| `POST` | `/api/v1/auth/magic-link` | Request magic link email *(501 — not built yet)* |
| `GET` | `/api/v1/auth/verify` | Verify magic link token *(501)* |
| `POST` | `/api/v1/auth/riot-id` | Link Riot ID to account *(501)* |
| `POST` | `/api/v1/dev/create-account` | Dev bypass — creates session instantly |

---

## CV pipeline (standalone — no web needed)

```powershell
cd services\cv
python main.py "path\to\clip.mp4"
# Output → services/cv/output/
```

Runs YOLO detection on every frame, produces an annotated video + JSON/CSV report with detected enemies, allies, and aiming mistake breakdown.

Train a new model:
```powershell
cd scripts
python train.py                      # uses data/ dataset, saves to services/cv/models/
```

---

## Keys

| Key | Where to get | Required for |
|---|---|---|
| `RIOT_API_KEY` | https://developer.riotgames.com | Match history + rank |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com | Coaching report (~$0.006/report) |
| `RESEND_API_KEY` | https://resend.com | Magic link email *(not built yet)* |
| `DATABASE_URL` | Neon or Supabase free tier | Persistent auth *(not built yet)* |
| `JWT_SECRET` | `openssl rand -hex 32` | JWT sessions *(not built yet)* |

> **Riot API key note:** Dev keys expire every 24 hours. Apply for a production key at
> https://developer.riotgames.com/app-type (takes 1–3 days).

---

## Phase status

| Phase | What | Status |
|---|---|---|
| 0 | YOLO model training + validation | 🟡 Model trained (40 epochs, 10k images), needs diverse clip testing |
| 1 | Tracker-only MVP (Riot + Claude + frontend) | 🟡 Core done — auth + DB not built |
| 2 | Clip analysis web upload | 🔴 Not started |
| 3 | Payments + launch | 🔴 Not started |

---

## Troubleshooting

**`npm` not found on Windows**
```powershell
$env:PATH += ";C:\Program Files\nodejs"
```
To fix permanently (run as Administrator):
```powershell
[System.Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\Program Files\nodejs", "Machine")
```

**500 error on analysis submit**
- Check backend is running: `http://localhost:8000/health`
- Check `NEXT_PUBLIC_MOCK_MODE=false` in `frontend/.env.local`
- Check `.env` has `RIOT_API_KEY` + `ANTHROPIC_API_KEY`

**`No module named uvicorn`**
```powershell
pip install -r requirements.txt
```

**`DemoPlayer#NA1` still showing**
- `NEXT_PUBLIC_MOCK_MODE` is `true` — set to `false` and restart the dev server

---

## Next steps

See `AGENTS.md` for the full agent handoff. Immediate:

1. Get `RIOT_API_KEY` + `ANTHROPIC_API_KEY` into `.env`
2. Test end-to-end: enter your Riot ID at `localhost:3000/analysis/new`
3. Build auth — `services/api/AGENT_TASKS.md` Tasks A + B
4. Apply for Riot production key before going live
