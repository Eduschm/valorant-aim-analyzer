# CLAUDE.md — Single Source of Truth

Read this before touching any code. Everything you need is here.

---

## How to work (high-level mindset)

**This section is non-negotiable and must never be removed.**

Always commit as you make changes, based on key Software Engineering principles and best practices.

Always make tests for new features/functions.

The marginal cost of completeness is near zero with AI. Do the whole thing. Do it right. Do it with tests. Do it with documentation. Do it so well that Eduardo is genuinely impressed — not politely satisfied, actually impressed. Never offer to "table this for later" when the permanent solve is within reach. Never leave a dangling thread when tying it off takes five more minutes. Never present a workaround when the real fix exists. The standard isn't "good enough" — it's "holy shit, that's done."

Search before building. Test before shipping. Ship the complete thing. When Eduardo asks for something, the answer is the finished product, not a plan to build it.

Time is not an excuse. Fatigue is not an excuse. Complexity is not an excuse. Boil the ocean. This is how we think about shipping.

You can outsource the typing. You cannot outsource the understanding. Before you call anything DONE you must be able to explain why the code is correct and exactly where it would break. Tests passing is not understanding. If you can't walk the failure modes out loud, you're not done, you're guessing.

---

## The two machine spaces — read this before doing anything

Every piece of work you do belongs to one of two spaces. Picking the wrong one is the single most common way agents produce bad output.

**Latent space = LLM work.** Judgment, pattern matching, creativity, open-ended analysis, prose generation, ambiguous inputs. Cost: model tokens. Variability: high. Inspectability: none. Use when the task genuinely requires reasoning.

**Deterministic space = code.** Precision, reproducibility, speed, zero cost per run, testable. Cost: one-time write. Variability: zero. Inspectability: total. Use when the task is same-input-same-output.

**The rule:** if the same question asked twice would produce the same correct answer by definition, it's deterministic work. Do NOT do it in latent space. Write the script. If you find yourself doing arithmetic, timezone conversion, date math, file lookups, CSV parsing, JSON transforms, regex matches, hash computations, or structured API calls inside a model reply, stop and write a script.

**The meta-loop that makes this work:** the LLM writes the deterministic script, then the script constrains the LLM forever after. The model's intelligence creates the constraint that prevents the model from being stupid. A bug in latent space becomes a feature in deterministic space, and the old failure path becomes structurally unreachable.

Every feature, every fix, every investigation starts with: is this latent or deterministic? If the answer is "both," split it. The deterministic piece becomes a script + tests. The latent piece becomes a prompt + eval.

---

## The context window is the lever

The context window is your only control surface over the model. Treat it as a deliberate input, not a dumping ground. Load the spec, the contract, the relevant files, and concrete examples. Leave the noise out. A vague or bloated context produces vague or bloated output, every time. When a task goes sideways, the first question is "what was in the window," not "was the model dumb." Curate before you prompt.

---

## Non-negotiable rules

### Tests and evals — every time, no exceptions

- Every feature ships with a test suite AND an eval suite, in the same commit. Not the next PR.
- Every bug fix ships with a test AND an eval that would have caught the bug. The regression test is the proof the bug is fixed. The eval is the proof the fix generalizes.
- Every failure gets skillified (the 10 steps). Same day. Same session when possible.
- "I'll add tests later" is banned. If the tests/evals aren't in the diff, the work isn't done.
- Two test lanes, different budgets:
  - **Gate tests** — deterministic, local, free, <2s. Run on every commit via pre-commit hook. Never flaky.
  - **Periodic evals** — paid (LLM calls), slower, quality-measuring. Run before ship and nightly. Allowed to be non-deterministic but must have a pass threshold.

### Tie every change to a measurable outcome

- Every feature names the outcome it moves before you build it: the metric, the workflow step, or the user-visible behavior that changes. "It works" is not an outcome.
- If you can't state what gets measurably better and how you'll see it, that's a Confusion Protocol stop, not a license to build.
- Wire in the trace. The change leaves evidence you can point at later: a metric, a log line, an eval score. Compute that produces no measurable, traceable result is theater.

### LLM access — local Claude Code, not the API

- When the software we build needs to call an LLM, do NOT use an LLM API (Anthropic API, OpenAI API, any hosted inference endpoint) unless Eduardo explicitly instructs it. Route the call through the local Claude Code instead.
- If no LLM service exists yet in the project, build one. Create a self-contained LLM service (under `services/llm/` per the architecture rules) that shells out to local Claude Code, with its own contract, tests, and evals. Every other service calls that contract, never an external API.
- Always use the best available model by default unless Eduardo explicitly instructs otherwise. No silent downgrades to a cheaper or smaller model for cost.

### Tech choice — vanilla by default

- Simplest vanilla tech wins. No framework-of-the-month. No clever abstractions for hypothetical reuse.
- Do not recreate what already exists. Before writing a utility, harness, or library, check for an existing lib that solves it.
- For cross-cutting concerns (eval harness, prompt library, vision utilities, observability, SEO, schema validation, etc.) grep GitHub in parallel for top candidates. Rank by stars, recency of last commit, issue responsiveness, and real user feedback (HN, Reddit, production write-ups). Return the best option with reasoning, not a list.
- If two options are equally viable, name the trade-off explicitly and ask Eduardo. Confusion Protocol applies.

### Search before building

Three layers, in order:

1. **Tried-and-true.** Is there a standard library or pattern that does this? Use it.
2. **New-and-popular.** Is there a newer library with real traction? Evaluate it.
3. **First-principles.** Does the conventional approach actually apply here? If our situation is genuinely different, document WHY before writing custom code.

Most of the time Layer 1 wins. Default to that. If Layer 3 produces a genuine insight contradicting conventional wisdom, log it as a note in the commit or a design doc.

### Check for skills

When a task matches a specialized domain (SEO, schema, security audit, design review, etc.), use the installed Claude Code skill. Don't reinvent what gstack or a community skill already does well. Invoke via the Skill tool, not by re-implementing.

### Skillify repeated success, not just failure

Failures get skillified — that rule already stands. So does repeated success. The second time you run the same manual flow by hand, stop and codify it: a script, a skill, or a workflow. One-off prompts don't compound; reusable flows do. The leverage is in the work you stop having to think about, not in re-prompting from scratch each time. Done it twice by hand? The third time is a command.

---

## Architecture — services-first, parallel-friendly

Build everything as independent services / self-contained directories. The goal: any single piece of the application can be worked on by a separate Claude Code session without stepping on another session's work.

- **One concern, one directory.** Each service lives under `services/<service-name>/` with its own code, tests, evals, and config. No shared mutable state across services beyond well-defined contracts.
- **Contracts at the boundary.** Services communicate via typed interfaces. Define the contract in `contracts/schemas.py` — never reach into another service's internals.
- **Independent test + eval suites.** Each service has its own gate tests and periodic evals. A change in one service must not require running another service's full suite to validate.
- **Independent deploy unit.** Each service builds and ships on its own. No monolithic release.
- **Parallel-session safe.** Two Claude sessions working in `services/foo/` and `services/bar/` should never collide. If a change requires coordinated edits across services, that's a contract change — bump the schema version, update both sides, call it out explicitly.
- **Top-level only holds glue.** Root directory: orchestration scripts, shared config, contracts, docs. No business logic.

**Fan out by default.** When a job decomposes into independent units, run them as separate isolated sessions or worktrees at the same time. Coordinate at the contract boundary, merge each unit when it's green.

### Common gotchas

```python
# WRONG — services must not import each other's internals
from services.riot.service import get_riot_report

# RIGHT — use the contract types
from contracts.schemas import RiotReport
```

Gate tests must run in <2s. Mock all external APIs. Slow tests belong in periodic evals.

---

## Completion status protocol

At the end of every task, report one of:

- **DONE** — All steps completed. Evidence provided for every claim. Tests + evals in the diff. Ready to merge.
- **DONE_WITH_CONCERNS** — Completed, but with issues Eduardo should know about. List each concern with severity and a proposed follow-up.
- **BLOCKED** — Cannot proceed. State what's blocking and what was already tried.
- **NEEDS_CONTEXT** — Missing information required to continue. State exactly what's needed.

"Partially done" is not a status. Either the feature ships (DONE) or it doesn't (BLOCKED / NEEDS_CONTEXT).

---

## After every task — commit, push, restart

Once a task is done, two things happen, no exceptions:

1. **Commit and push.** Stage the work, write a clear commit message, push to GitHub. Don't wait to be asked. Respects Safety rules (no secrets, no `--no-verify`, no destructive ops without confirmation).
2. **Report what to restart.** Tell Eduardo exactly which service / system / program needs to be restarted for the change to take effect, with the full list of commands to run. If nothing needs restarting, say so explicitly.

For restart commands that need `sudo`: never run them yourself. List them for Eduardo to run.

---

## Confusion protocol

When you hit high-stakes ambiguity:

- Two plausible architectures for the same requirement
- A request that contradicts an existing pattern
- A destructive operation with unclear scope
- Missing context that would materially change the approach

STOP. Name the ambiguity in one sentence. Present 2-3 options with real trade-offs. Ask Eduardo. Does not apply to routine coding, small features, or obvious changes.

---

## Safety

- Never commit secrets. If `.env` is touched, verify `.gitignore` before any commit.
- Never run `rm -rf`, `git reset --hard`, `git push --force`, `DROP TABLE`, `kubectl delete`, or similar destructive ops without explicit confirmation.
- Never skip pre-commit hooks with `--no-verify`. If a hook fails, fix the underlying issue.
- Never commit binaries, compiled outputs, or model weights to the repo. Use Git LFS or cloud storage with a pointer.
- Before any action that touches production, state what you're about to do, wait for confirmation.

---

## How Eduardo wants to be talked to

- Direct. Short. Concrete. No preamble.
- Specific file names, function names, line numbers. Not "there's an issue in the classifier" — it's `food_vision/classifier.py:47`.
- No em dashes. No AI vocabulary (delve, crucial, robust, comprehensive, nuanced, multifaceted, furthermore, moreover, pivotal, landscape, tapestry, underscore, foster, showcase, intricate, vibrant, fundamental, significant, interplay).
- No banned phrases: "here's the kicker", "here's the thing", "plot twist", "let me break this down", "the bottom line", "make no mistake".
- If something is broken, say so plainly.
- End responses with the next action, not a recap of what was just done.

When Eduardo asks for something, the answer is the finished product — not a plan. Tests included. Evals included. Docs included.

---

## Product

SaaS that analyzes Valorant gameplay. Phase 1: Riot API stats + AI coaching. Phase 2: YOLO clip analysis. Phase 3: payments + launch.

Solo founder. Success threshold: $200/month (~20 paying users at $9/month) in 3 months.

### What it does

1. Pulls the last 20 ranked matches from the Riot API
2. Extracts headshot %, ADR, win rate, top agent/weapon, rank delta
3. Feeds stats to Claude Haiku → personalised, number-specific coaching report
4. *(Phase 2)* Runs YOLO on uploaded clips → detects overshoot, undershoot, body-not-head, spray control failures

---

## Project structure

```
valorant-aim-analyzer/
├── services/
│   ├── api/          FastAPI REST API — routes, job dispatch, auth stubs
│   ├── riot/         Riot API client + match parser
│   ├── llm/          Claude coaching report generator
│   └── cv/           YOLO video analysis (Phase 2)
├── contracts/        Shared type definitions (schemas.py)
├── frontend/         Next.js 14 web app (App Router)
├── scripts/          Training + labeling utilities
├── CLAUDE.md         This file — read before touching anything
├── .env              Local config (secrets, API keys) — gitignored
├── pytest.ini        Python test configuration
├── requirements.txt  All Python dependencies
└── dev.ps1, dev-frontend.ps1   Startup scripts
```

Service dependency graph:
```
frontend → api
            ↓
          riot  (fetches Valorant data)
          llm   (generates coaching)
          cv    (analyzes video — Phase 2)
```

**Contract boundary**: All inter-service communication via `contracts/schemas.py`. No service imports another's internals.

---

## Current service status

| Service | Status | Entry point | Notes |
|---|---|---|---|
| `services/cv` | Done | `python main.py clip.mp4` | Standalone YOLO pipeline. Needs `models/valorant.pt`. |
| `services/riot` | Done | `service.py → get_riot_report()` | Full implementation. Needs `RIOT_API_KEY`. Dev key expires every 24h. |
| `services/llm` | Done | `coach.py → generate_coaching_report()` | Full implementation. Needs `ANTHROPIC_API_KEY`. ~$0.006/call. |
| `services/api` | Partial | `uvicorn main:app --port 8000` | `/analyze` + `/report/{id}` work. Auth routes return 501. In-memory store only. |
| `frontend` | Done | `npm run dev` → port 3000 | All pages built. Mock + real mode both work. |

### Frontend pages

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

## Analysis pipeline

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

## Contracts (`contracts/schemas.py`)

All inter-service types live here. Never import from one service's internals into another.

```python
@dataclass
class RiotReport:
    puuid: str
    game_name: str
    tag_line: str
    current_rank: str | None
    rank_delta: int | None
    matches: list[MatchStat]
    avg_headshot_pct: float
    avg_adr: float
    top_agent: str
    win_rate: float

@dataclass
class CVReport:
    video_name: str
    total_frames: int
    fps: float
    detections: dict[str, int]
    engagement_windows: list[dict]

@dataclass
class CoachingReport:
    summary: str
    top_weakness: str
    tips: list[str]
    encouragement: str
    raw_response: str

@dataclass
class AnalysisResult:
    report_id: str
    status: str  # "queued" | "processing" | "done" | "error"
    riot_report: RiotReport | None
    cv_report: CVReport | None
    coaching: CoachingReport | None
    error: str | None
```

When adding fields: add with a default value, bump the schema version in the docstring, update all consumers simultaneously.

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

## Service details

### services/api

- **Entry point**: `main.py` — FastAPI application
- **In-memory store**: `store.py` — temporary analysis results (replaced by DB when auth is built)
- **Schemas**: `schemas.py` — request/response Pydantic types
- **Tests**: `tests/test_api.py`
- **Dependencies**: FastAPI, Uvicorn, Pydantic, httpx, python-dotenv

```bash
python -m pytest services/api/tests/ -v
```

### services/riot

- **Entry point**: `service.py` → `get_riot_report(riot_id, region, match_count)`
- **Client**: `client.py` — async HTTP with tenacity retry (3 attempts, exponential backoff)
- **Parser**: `parser.py` — raw Riot API JSON → typed structures
- **Tests**: `tests/test_parser.py` — 8 gate tests, all mocked

Known limitations:
- Weapon extraction uses UUID from `finishingDamage.damageItem`, not human names
- ADR is approximated as `score / numberOfRounds` (Riot doesn't expose damage per round in match-v1)
- Default region is `na` — pass `region="eu"` etc. to change

```bash
python -m pytest services/riot/tests/ -v
```

### services/llm

- **Entry point**: `coach.py` → `generate_coaching_report(riot_report, cv_report=None)`
- **Model**: `claude-haiku-4-5` (from `LLM_MODEL` env var)
- **Cost**: ~$0.006 per report
- **Tests**: `tests/test_coach.py` — 4 gate tests, mocked Anthropic client

`build_prompt()` constructs a structured prompt with exact numbers (rank, HS%, ADR, per-match K/D/A). System prompt instructs Claude to respond in JSON only:
```json
{
  "summary": "2-3 sentences with specific stats",
  "top_weakness": "single biggest issue with a stat reference",
  "tips": ["3-5 actionable tips, each with a number"],
  "encouragement": "one closing line"
}
```
Auto-retries once on JSON parse failure.

```bash
python -m pytest services/llm/tests/ -v
```

### services/cv

- **Entry point**: `main.py` — CLI for video processing
- **Status**: MVP only. YOLO detection works. Web integration pending (Phase 2).
- **Models**: `models/valorant.pt` (custom) or `yolov8n` fallback

```bash
cd services/cv
python main.py path/to/video.mp4 --device 0
# Output → services/cv/output/video_report.json + video_events.csv
```

```bash
python -m pytest services/cv/tests/ -v --ignore=services/cv/tests/test_detector.py
```

### frontend

- **Framework**: Next.js 14+ App Router
- **Styling**: Tailwind CSS
- **State**: Zustand (`lib/store.ts`) + localStorage (`lib/storage.ts`)
- **Testing**: Vitest + React Testing Library
- **HTTP**: Native fetch (`lib/api.ts`)

localStorage persistence (`frontend/lib/storage.ts`):
- `saveAnalysis(report)` — called by report page on completion
- `getAllAnalyses()` — used by Dashboard, Profile
- `getAnalyses(riotId)` — used by Tracker
- `clearAnalyses()` — called by sign out

Max 20 entries per Riot ID. No backend needed for Dashboard/Tracker/Profile pages.

```bash
cd frontend && npm test
```

---

## Remaining work — priority order

### 1. Auth + DB — Tasks A + B (HIGH — blocks accounts, free tier, paid tier)

**Task A: Database (replaces in-memory store)**

Requires: `DATABASE_URL` (Neon https://neon.tech or Supabase https://supabase.com free tier)

1. Create `services/api/database.py` with SQLAlchemy async engine + `Base`
2. Create `services/api/models.py` with `User`, `MagicToken`, `Report` ORM tables
3. Replace `store.InMemoryStore` in `main.py` with async DB calls
4. Run `alembic init alembic` and create the initial migration

**Task B: Auth — magic link + JWT**

Requires: `RESEND_API_KEY` (https://resend.com, 100/day free), `JWT_SECRET` (`openssl rand -hex 32`)

Create `services/api/auth.py`:
- `create_magic_link(email, db)` — get/create User, create MagicToken (15 min expiry), send via Resend
- `verify_token(token, db)` — validate token, mark used, return JWT (7-day expiry)
- `get_current_user(request, db)` — FastAPI dependency, reads `auth_token` cookie

Wire into `main.py`:
- `POST /api/v1/auth/magic-link` → `create_magic_link`
- `GET /api/v1/auth/verify?token=xxx` → `verify_token` → set httpOnly cookie → redirect to `/`
- `POST /api/v1/auth/riot-id` → require auth, validate via `get_riot_report`, save to user

### 2. Rate limiting + credit tracking — Tasks C + D (LOW — depends on Task A)

**Task C: Rate limiting**
```bash
pip install slowapi
```
Apply `@limiter.limit("10/minute")` on `POST /api/v1/analyze`.

**Task D: Free tier enforcement**

In `submit_analysis`: check `user.credits_used >= 10`, raise HTTP 429 if over limit, increment on each call. Reset monthly.

### 3. Wire frontend auth state (LOW — depends on Tasks A + B)

`frontend/lib/store.ts` has `useAuthStore` defined but nothing calls `setUser()`. Add `GET /api/v1/me` endpoint and call it on app load to hydrate the auth store.

### 4. Apply for Riot production key (ADMIN — no code)

Dev key expires every 24h and will break the live product on day one. Apply at https://developer.riotgames.com/app-type (takes 1-3 business days).

### 5. Phase 2: Clip upload (HIGH complexity — do not start until Phase 1 has paying users)

- Drag-and-drop upload (3 min, ~200MB cap)
- Server-side FFmpeg frame extraction at 5fps
- CV service processes frames → engagement stats
- Merge CV report with Riot report before LLM call
- Async queue (BackgroundTasks → Celery when needed)

### 6. Phase 3: Payments (MEDIUM — do not start until Phase 1 has paying users)

Stripe integration, credit-based. Free: 10/month. Paid: $9/month, unlimited.

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

Desktop client, CS2/Apex, team/coach accounts, replay file parsing, mobile app, Discord bot, live coaching, custom drill generation beyond Claude output.

---

## Phase status

| Phase | What | Status |
|---|---|---|
| 0 | YOLO model training + validation | Model trained (40 epochs, 10k images), needs diverse clip testing |
| 1 | Tracker-only MVP (Riot + Claude + frontend) | Core done — auth + DB not built |
| 2 | Clip analysis web upload | Not started |
| 3 | Payments + launch | Not started |

---

## Quick start

### Environment

Copy `.env.example` to `.env` and fill in:
```
RIOT_API_KEY=RGAPI-...        # https://developer.riotgames.com
ANTHROPIC_API_KEY=sk-ant-...  # https://console.anthropic.com
DEV_MODE=true
```

Frontend config (`frontend/.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MOCK_MODE=false
NEXT_PUBLIC_LOG_LEVEL=debug
```

### Run backend

```powershell
.\dev.ps1
```

Starts FastAPI on `http://localhost:8000` with auto-reload.

### Run frontend (separate terminal)

```powershell
.\dev-frontend.ps1
```

Starts Next.js on `http://localhost:3000`.

If you get permission errors running `.ps1` files:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Install dependencies

```powershell
pip install -r requirements.txt   # Python services
cd frontend && npm install          # Frontend
```

### Dev bypass (no email or database needed)

**Option A — UI:** Go to `/auth/signin` → click "Skip auth → go straight to analysis"

**Option B — curl:**
```bash
curl -X POST http://localhost:8000/api/v1/dev/create-account \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@localhost"}'
```

Requires `DEV_MODE=true` in `.env`.

### Testing

```powershell
# Backend (all services)
python -m pytest services/ -v --ignore=services/cv/tests/test_detector.py

# Single service
python -m pytest services/api/tests/ -v

# Frontend
cd frontend && npm test
```

---

## How to start work on a task

1. **Pick a task** from the Remaining work section above (ordered by priority).
2. **Name the outcome** — what metric moves, what workflow step changes, what user-visible behavior improves. Don't start if you can't name it.
3. **Write gate tests first** in `services/<service>/tests/test_<feature>.py`. Arrange → Act → Assert. Mock external deps. <100ms per test.
4. **Implement** within one service when possible. Cross-service changes = contract change.
5. **Run the full suite** and verify the outcome is measurable.
6. **Commit** with conventional message (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
7. **Report** what needs restarting.

### Working on services

**API changes**: define contract in `contracts/schemas.py` → write test → add endpoint in `services/api/main.py` → run tests → commit → restart backend.

**Riot service**: write test → update `service.py` / `parser.py` → run tests → commit. No restart needed (pure function).

**LLM service**: write test → update `coach.py` → run tests → commit. No restart needed.

**Frontend**: write test in `frontend/__tests__/` → add component/page → run tests → dev server → commit.

---

## Troubleshooting

**`npm` not found on Windows**
```powershell
$env:PATH += ";C:\Program Files\nodejs"
```

**500 error on analysis submit**
- Check backend is running: `http://localhost:8000/health`
- Check `NEXT_PUBLIC_MOCK_MODE=false` in `frontend/.env.local`
- Check `.env` has `RIOT_API_KEY` + `ANTHROPIC_API_KEY`
- Run: `python -m pytest services/api/tests/ -v`

**`No module named uvicorn`**
```powershell
pip install -r requirements.txt
```

**`DemoPlayer#NA1` still showing**
- `NEXT_PUBLIC_MOCK_MODE` is `true` — set to `false` and restart dev server.

**Import errors in Python**
- Check repo root: `cd c:\Users\Edu\Desktop\T\valorant-aim-analyzer`
- Activate venv: `. .venv/Scripts/Activate.ps1`
- Reinstall: `pip install -r requirements.txt`

**Riot API key expired**
- Dev keys expire every 24h. Get a new one at https://developer.riotgames.com or apply for production key.

**Tests fail locally but pass in CI**
- Check Python version (must be 3.10+): `python --version`
- Ensure venv activated: `. .venv/Scripts/Activate.ps1`

---

## Required keys

| Key | Where to get | Required for |
|---|---|---|
| `RIOT_API_KEY` | https://developer.riotgames.com | Match history + rank |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com | Coaching report (~$0.006/report) |
| `RESEND_API_KEY` | https://resend.com | Magic link email (not built yet) |
| `DATABASE_URL` | Neon or Supabase free tier | Persistent auth (not built yet) |
| `JWT_SECRET` | `openssl rand -hex 32` | JWT sessions (not built yet) |
