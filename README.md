# AimLab VAL — Valorant Aim Analyzer

AI-powered aim analysis for Valorant. Paste a Riot ID, get a coaching report.

---

## What it does

1. Pulls the last 20 matches from the Riot API
2. Extracts headshot %, ADR, win rate, top agent/weapon, rank delta
3. Feeds stats to Claude Haiku → personalised coaching report
4. (Phase 2) Runs YOLO on uploaded clips → identifies overshoot, undershoot, body-not-head, spray control errors

---

## Project structure

```
valorant-aim-analyzer/
├── contracts/schemas.py          shared typed contracts (all services import from here)
├── services/
│   ├── cv/                       YOLO video analysis — DONE
│   ├── riot/                     Riot API client + parser — DONE (needs RIOT_API_KEY)
│   ├── llm/                      Claude coaching — DONE (needs ANTHROPIC_API_KEY)
│   └── api/                      FastAPI backend — core done, auth stubbed
├── frontend/                     Next.js app — DONE (mock + real mode)
├── scripts/                      train.py, label_tool.py, Colab notebook
├── data/                         training dataset (gitignored)
├── AGENTS.md                     agent handoff doc — read this before building anything
└── .env.example                  copy to .env, fill in keys
```

---

## Running locally

### Frontend (mock mode — no backend needed)

```powershell
cd frontend
$env:PATH += ";C:\Program Files\nodejs"   # Windows only if npm not on PATH
npm install
npm run dev    # → http://localhost:3000
```

`NEXT_PUBLIC_MOCK_MODE=true` in `frontend/.env.local` returns fixture data.
Set to `false` to hit the real API.

### Backend

```bash
cp .env.example .env   # fill in RIOT_API_KEY and ANTHROPIC_API_KEY

cd services/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Dev account bypass (no email needed)

With `DEV_MODE=true` in `.env`, click **"Skip auth"** on the sign-in page,
or call the endpoint directly:

```bash
curl -X POST http://localhost:8000/api/v1/dev/create-account \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@localhost"}'
```

### CV pipeline (standalone)

```bash
cd services/cv
python main.py "path/to/clip.mp4"
# → services/cv/output/
```

---

## Keys needed

| Key | Where | Required for |
|---|---|---|
| `RIOT_API_KEY` | https://developer.riotgames.com | Riot stats |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com | Coaching report |
| `RESEND_API_KEY` | https://resend.com | Magic link email |
| `DATABASE_URL` | Neon / Supabase free tier | Persistent auth |

---

## Phase status

| Phase | What | Status |
|---|---|---|
| 0 | YOLO model validation | 🟡 Model trained, needs diverse clip testing |
| 1 | Tracker-only MVP | 🟡 Core done, auth + DB not built |
| 2 | Clip analysis web upload | 🔴 Not started |
| 3 | Payments + launch | 🔴 Not started |

---

## Next steps

See `AGENTS.md` for full agent handoff. Immediate priorities:

1. Add `RIOT_API_KEY` + `ANTHROPIC_API_KEY` to `.env`
2. Test: `POST /api/v1/analyze` with a real Riot ID
3. Build auth (DB + magic link) → `services/api/AGENT_TASKS.md` Tasks A + B
4. Apply for Riot production key (dev key expires every 24h) → https://developer.riotgames.com/app-type
