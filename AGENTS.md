# Agent Handoff Document

Read this before touching any code. Single source of truth for project state.

---

## Product

SaaS that analyzes Valorant gameplay. Phase 1: Riot API stats + AI coaching.
Phase 2: YOLO clip analysis. Phase 3: payments + launch.

Solo founder. Success threshold: $200/month (~20 paying users at $9/month) in 3 months.

---

## Current service status

| Service | Status | Entry point | Notes |
|---|---|---|---|
| `services/cv` | ✅ Done | `python main.py clip.mp4` | Standalone YOLO pipeline. Needs `models/valorant.pt`. |
| `services/riot` | ✅ Done | `service.py → get_riot_report()` | Full implementation. Needs `RIOT_API_KEY`. Dev key expires every 24h. |
| `services/llm` | ✅ Done | `coach.py → generate_coaching_report()` | Full implementation. Needs `ANTHROPIC_API_KEY`. ~$0.006/call. |
| `services/api` | 🟡 Partial | `uvicorn main:app --port 8000` | `/analyze` + `/report/{id}` work. Auth routes return 501. In-memory store only. |
| `frontend` | ✅ Done | `npm run dev` → port 3000 | All pages built. Mock + real mode both work. |

---

## Frontend pages (all built)

| Page | Path | Notes |
|---|---|---|
| Landing | `/` | Premium dark, single CTA |
| Analysis input | `/analysis/new` | Riot ID autocomplete, region selector, last-used chip |
| Report | `/analysis/[id]` | Polls API, saves to localStorage on done |
| Tracker | `/tracker` | Rank chart, stat trends, sortable match log |
| Profile | `/profile` | Identity, progress deltas, usage bar |
| Dashboard | `/dashboard` | History table (from localStorage), quick stats |
| Settings | `/settings` | Riot ID link, dev bypass, sign out |
| Sign in | `/auth/signin` | Magic link form + dev bypass button |

---

## How the analysis pipeline works

```
User submits Riot ID at /analysis/new
  → POST /api/analysis/tracker (Next.js route)
  → POST /api/v1/analyze (FastAPI)
  → background task:
      get_riot_report(riot_id)        [services/riot/service.py]
      generate_coaching_report(riot)  [services/llm/coach.py]
  → store result in memory
  → GET /api/v1/report/{id} polled every 3s
  → frontend saves to localStorage when done
  → Tracker/Profile pages read from localStorage
```

---

## Contracts

`contracts/schemas.py` — all inter-service types. **Never import from one service's internals into another.**

Key types: `RiotReport`, `CVReport`, `CoachingReport`, `AnalysisResult`, `MatchStat`.

---

## localStorage persistence

`frontend/lib/storage.ts` — analysis results stored by Riot ID.

- `saveAnalysis(report)` — called by report page on completion
- `getAllAnalyses()` — used by Dashboard, Profile
- `getAnalyses(riotId)` — used by Tracker
- `clearAnalyses()` — called by sign out

Max 20 entries per Riot ID. No backend needed for these pages.

---

## Remaining work — priority order

### 1. Auth + DB — `services/api/AGENT_TASKS.md` Tasks A + B

**Complexity: High. Blocks: accounts, free tier, paid tier.**

- Task A: SQLAlchemy models (User, MagicToken, Report) + Alembic migration + async DB session
- Task B: Magic link flow — Resend email → `/auth/verify` → JWT httpOnly cookie → `get_current_user` dependency

Requires env vars: `DATABASE_URL`, `RESEND_API_KEY`, `JWT_SECRET`, `EMAIL_FROM`.

Get DB free at Neon (https://neon.tech) or Supabase (https://supabase.com).
Get email free at Resend (https://resend.com, 100/day free).

### 2. Rate limiting + credit tracking — `services/api/AGENT_TASKS.md` Tasks C + D

**Complexity: Low. Depends on Task A.**

- `slowapi`: 10 req/min on `/analyze`
- `User.credits_used` incremented per analysis, gated at 10/month for free tier

### 3. Wire frontend auth state

**Complexity: Low. Depends on Tasks A + B.**

`frontend/lib/store.ts` has `useAuthStore` defined but nothing calls `setUser()`.
Once `/auth/verify` works and returns a JWT cookie, add a `GET /api/v1/me` endpoint
and call it on app load to hydrate the auth store.

### 4. Apply for Riot production key

**Admin task. No code.**

Dev key expires every 24h and will break the live product on the first day.
Apply at https://developer.riotgames.com/app-type — takes 1–3 business days.

### 5. Phase 2: Clip upload

**Complexity: High. Do not start until Phase 1 has paying users.**

- Drag-and-drop upload (3 min, ~200MB cap)
- Server-side FFmpeg frame extraction at 5fps
- CV service (`services/cv/main.py`) processes frames → engagement stats
- Merge CV report with riot report before LLM call
- Async queue (start with BackgroundTasks, upgrade to Celery when needed)

### 6. Phase 3: Payments

**Complexity: Medium. Do not start until Phase 1 has paying users.**

- Stripe integration — credit-based
- Free: 10 analyses/month. Paid: $9/month, unlimited.
- `services/api/AGENT_TASKS.md` has Stripe wiring notes.

---

## Key decisions — do not revisit

- Screen center = crosshair. No crosshair detection needed in CV pipeline.
- Phase 1 ships without clip analysis.
- Claude Haiku 4.5 for production LLM.
- Magic link email auth, no passwords.
- Riot ID = account identifier (prevents multi-account free tier abuse).
- In-memory store for MVP — replace with DB only when auth is built.
- No Redis queue until background processing exceeds 10s.
- 3-minute clip cap, free tier.
- 7-day trial instead of money-back guarantee.
- Freemium: 10 free / $9 paid.

---

## Out of scope (first 3 months)

Desktop client, CS2/Apex, team/coach accounts, replay file parsing, mobile app,
Discord bot, live coaching, custom drill generation beyond Claude output.

---

## Environment quick-start

```bash
# Copy and fill in
cp .env .env.local    # or just edit .env directly

# Minimum to run the full pipeline:
RIOT_API_KEY=RGAPI-...
ANTHROPIC_API_KEY=sk-ant-...
DEV_MODE=true
```

```powershell
# Backend (separate terminal)
cd services\api
python -m uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
$env:PATH += ";C:\Program Files\nodejs"
npm run dev
```

Set `NEXT_PUBLIC_MOCK_MODE=false` in `frontend/.env.local` to use real API.
