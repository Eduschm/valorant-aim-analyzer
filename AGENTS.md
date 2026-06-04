# Agent Handoff Document
## Valorant Aim Analyzer

Start here. Read this before touching any code.

---

## Product summary

SaaS that analyzes Valorant gameplay. Phase 1: Riot API stats + AI coaching report.
Phase 2: YOLO clip analysis. Phase 3: payments + launch.

Target: $200/month profit in 3 months (~20 paying users at $9/month).

---

## Repo structure

```
valorant-aim-analyzer/
├── contracts/schemas.py       ← shared typed contracts — all services import from here
├── services/
│   ├── cv/                    ← YOLO video analysis (DONE — working)
│   ├── riot/                  ← Riot API client (STUBBED — needs implementation)
│   ├── llm/                   ← Claude coaching (STUBBED — needs implementation)
│   └── api/                   ← FastAPI backend (STUBBED — needs implementation)
├── frontend/                  ← Next.js app (BUILT — working in mock mode)
├── scripts/                   ← training utilities
├── data/                      ← training dataset (gitignored)
└── .env.example               ← copy to .env, fill in keys
```

---

## Service status

| Service | Status | Task doc |
|---|---|---|
| `services/cv` | ✅ Done | — |
| `services/riot` | ✅ Done (needs RIOT_API_KEY to run) | `services/riot/AGENT_TASKS.md` |
| `services/llm` | ✅ Done (needs ANTHROPIC_API_KEY to run) | `services/llm/AGENT_TASKS.md` |
| `services/api` | 🟡 Core done, auth stubbed | `services/api/AGENT_TASKS.md` |
| `frontend` | 🟡 Built (mock mode) | `frontend/PLAN.md` |

---

## Contracts (read before building anything)

`contracts/schemas.py` defines all inter-service types:

- `RiotReport` — output of riot service
- `CVReport` — output of cv service
- `CoachingReport` — output of llm service
- `AnalysisResult` — combined result returned by API

**Rule:** services never import each other's internals. They only import from `contracts/`.

---

## Build order

Build in this sequence. Each step depends on the previous.

```
1. services/riot   →  produces RiotReport
2. services/llm    →  consumes RiotReport, produces CoachingReport
3. services/api    →  wires riot + llm, exposes HTTP, owns DB + auth
4. frontend        →  connect mock mode → real API (change NEXT_PUBLIC_MOCK_MODE=false)
```

---

## Environment setup

```bash
cp .env.example .env
# Fill in: RIOT_API_KEY, ANTHROPIC_API_KEY, DATABASE_URL, JWT_SECRET, RESEND_API_KEY
```

Each service has its own venv:
```bash
cd services/riot && python -m venv .venv && .venv/Scripts/activate && pip install -r requirements.txt
cd services/llm  && python -m venv .venv && .venv/Scripts/activate && pip install -r requirements.txt
cd services/api  && python -m venv .venv && .venv/Scripts/activate && pip install -r requirements.txt
```

---

## Running locally

```bash
# Backend
cd services/api
uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm run dev     # → http://localhost:3000
```

Set `NEXT_PUBLIC_MOCK_MODE=false` in `.env.local` once the API is running.

---

## Key decisions (settled — do not revisit)

- Screen centre = crosshair. No crosshair detection needed in CV pipeline.
- Phase 1 ships without clip analysis (tracker stats only).
- Free tier: 10 analyses/month. Paid: $9/month unlimited.
- Riot ID = account identifier (one free account per Riot ID).
- Magic link email auth only — no passwords.
- Claude Haiku 4.5 for production LLM (~$0.006/report).
- No Redis queue in MVP — run analysis inline. Add queue when >10s processing.
- 3-minute clip cap for free tier (Phase 2).

---

## What NOT to build (Phase 1)

- Desktop client
- CS2/Apex support
- Team/coach accounts
- Replay file parsing
- Mobile app
- Discord bot
- Stripe/payments (Phase 3 only)
- Dashboard/history (Phase 3 only)

---

## Immediate next actions (in order)

1. Get your keys into `.env` (copy `.env.example` → `.env`):
   - `RIOT_API_KEY` — https://developer.riotgames.com (dev key, apply for prod key too)
   - `ANTHROPIC_API_KEY` — https://console.anthropic.com
2. Test end-to-end: `cd services/api && uvicorn main:app --reload`
   then `POST /api/v1/analyze` with your Riot ID
3. Implement auth (DB + magic link) — see `services/api/AGENT_TASKS.md` Tasks A+B
4. Set `NEXT_PUBLIC_MOCK_MODE=false` in `frontend/.env.local` and test frontend → API
5. Soft launch to 5 test users
