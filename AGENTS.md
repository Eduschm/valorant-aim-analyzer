# Agent Handoff Document

Read this before touching any code. It is the single source of truth for project state.

---

## Product

SaaS that analyzes Valorant gameplay. Phase 1: Riot API stats + AI coaching.
Phase 2: YOLO clip analysis. Phase 3: payments + launch.

Solo founder. Success threshold: $200/month profit in 3 months (~20 paying users).

---

## Service status

| Service | Status | Entry point | Notes |
|---|---|---|---|
| `services/cv` | ✅ Done | `main.py` | Runs standalone. Needs `models/valorant.pt`. |
| `services/riot` | ✅ Done | `service.py → get_riot_report()` | Needs `RIOT_API_KEY` to run. Dev key expires every 24h. |
| `services/llm` | ✅ Done | `coach.py → generate_coaching_report()` | Needs `ANTHROPIC_API_KEY`. |
| `services/api` | 🟡 Partial | `main.py` → uvicorn port 8000 | `/analyze` + `/report/{id}` work. Auth returns 501. |
| `frontend` | ✅ Done | `npm run dev` port 3000 | Mock mode (`NEXT_PUBLIC_MOCK_MODE=true`) and real mode both work. |

---

## Contracts

`contracts/schemas.py` — all inter-service types. Never import service internals across services.

Key types: `RiotReport`, `CVReport`, `CoachingReport`, `AnalysisResult`.

---

## What works right now

```
POST /api/v1/analyze  {"riot_id": "Name#TAG"}
→ background task: get_riot_report() → generate_coaching_report()
→ GET /api/v1/report/{id} polls until done
→ frontend report page displays result
```

Requires `RIOT_API_KEY` + `ANTHROPIC_API_KEY` in `.env`. Set `DEV_MODE=true` for account bypass.

---

## Remaining work — in priority order

### 1. Auth + DB (`services/api/AGENT_TASKS.md` Tasks A + B)

**Complexity: High. Blocks: user accounts, free tier limits, paid tier.**

- Task A: PostgreSQL models (User, MagicToken, Report) + Alembic migration
- Task B: Magic link auth (`/auth/magic-link` → Resend email → `/auth/verify` → JWT cookie)

Requires: `DATABASE_URL` (Neon/Supabase free tier), `RESEND_API_KEY`, `JWT_SECRET`.

### 2. Rate limiting + credit tracking (`services/api/AGENT_TASKS.md` Tasks C + D)

**Complexity: Low. Depends on Task A (DB).**

- `slowapi` 10 req/min on `/analyze`
- Free tier: 10 analyses/month per user, tracked in `User.credits_used`

### 3. Wire frontend auth to real API

**Complexity: Low. Depends on Tasks A + B.**

- Sign-in form already exists. Just needs `/api/v1/auth/magic-link` to return 200 (not 501).
- Set `NEXT_PUBLIC_MOCK_MODE=false` in `frontend/.env.local`.

### 4. Riot production key

**Complexity: Admin task. No code needed.**

Apply at https://developer.riotgames.com/app-type — takes 1-3 days.
Dev key expires every 24h and will break the live product.

### 5. Phase 2: Clip upload

**Complexity: High. Do not start until Phase 1 has paying users.**

- Web upload form (3 min cap, drag-and-drop)
- FFmpeg frame extraction → CV service → results merged with riot report
- Async queue (Celery or Redis)

### 6. Phase 3: Payments

**Complexity: Medium. Do not start until Phase 1 has paying users.**

- Stripe integration, credit-based billing
- Free tier: 10/month. Paid: $9/month.
- `services/api/AGENT_TASKS.md` has Stripe setup notes.

---

## Key decisions — settled, do not revisit

- Screen center = crosshair. No crosshair detection needed.
- Phase 1 ships without clip analysis.
- Haiku 4.5 for production LLM.
- Magic link email auth, no passwords.
- Riot ID = account identifier (prevents multi-account abuse).
- In-memory store for MVP — replace with DB when auth is built.
- No Redis queue until processing exceeds 10s.
- 3-minute clip cap, free tier.
- 7-day trial instead of money-back guarantee.

---

## Out of scope (first 3 months)

Desktop client, CS2/Apex support, team accounts, replay parsing, mobile, Discord bot, live coaching, custom drills beyond Claude output.

---

## Environment

```bash
cp .env.example .env
# Minimum to run: RIOT_API_KEY, ANTHROPIC_API_KEY, DEV_MODE=true
```

Each service has its own `requirements.txt`. Install per service:
```bash
cd services/api && pip install -r requirements.txt
cd services/riot && pip install -r requirements.txt
cd services/llm && pip install -r requirements.txt
```

Run:
```bash
# Backend
cd services/api && uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm run dev
```
