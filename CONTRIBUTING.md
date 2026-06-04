# Working on Valorant Aim Analyzer

Before building anything, read these in order:
1. [CLAUDE.md](CLAUDE.md) — Development principles (non-negotiable)
2. [AGENTS.md](AGENTS.md) — Product spec and current status
3. [README.md](README.md) — Quick overview
4. This file — How to structure work

---

## Key Principles from CLAUDE.md

### Services-First Architecture
- Each service under `services/` is independent: own code, tests, config, README
- Services communicate **only** via typed contracts in `contracts/schemas.py`
- Never import from another service's internals
- Two Claude sessions can work in `services/api/` and `services/riot/` in parallel without colliding

### Tests + Evals, Every Time
- Every feature ships with gate tests (local, fast, deterministic)
- Gate tests run on every commit via pre-commit hook
- No "I'll add tests later" — if tests aren't in the diff, the work isn't done
- All tests must pass before committing

### Latent vs Deterministic Space
- **Deterministic** (scripting, data transforms, file ops, arithmetic): Write a script, not prose
- **Latent** (judgment, creativity, reasoning): Use the LLM
- Split tasks that are "both" — deterministic becomes script + tests, latent becomes prompt

### Completion Status
At end of task, report one of:
- **DONE** — All steps completed, tests + evals included, ready to merge
- **DONE_WITH_CONCERNS** — Completed but with known issues
- **BLOCKED** — Cannot proceed, state what's blocking
- **NEEDS_CONTEXT** — Missing information required

"Partially done" is not an option. Either ships or doesn't.

### Commit + Restart
After every task:
1. Commit changes with clear conventional commit message (feat:, fix:, docs:, etc.)
2. List what needs restarting for changes to take effect
3. Do not ask permission to commit — just do it

---

## How to Start Work

### 1. Pick a Task
From [AGENTS.md](AGENTS.md), tasks are prioritized:
- **Phase 1**: Auth + DB (highest priority)
- **Phase 2**: Rate limiting + credit tracking
- **Phase 3**: Wire frontend auth state
- ... and so on

### 2. Define Your Outcome
Before coding, answer:
- What metric does this move?
- What workflow step changes?
- What user-visible behavior improves?
- How will you see it's working?

Don't start if you can't name the outcome. If stuck, use Confusion Protocol (stop, name the ambiguity, ask).

### 3. Write Tests First (Gate Tests)
Before touching service code:
```bash
cd services/<service>/tests/
# Create test_<feature>.py with:
# - Clear test name (test_does_what_when_what)
# - Arrange → Act → Assert pattern
# - Mocks for external dependencies
# - Fast (<100ms per test)
```

Example:
```python
def test_submit_analysis_queues_background_task(client):
    """Submitting analysis creates a report and queues processing."""
    response = client.post("/api/v1/analyze", json={"riot_id": "Player#NA1"})
    assert response.status_code == 200
    assert "report_id" in response.json()
```

### 4. Implement the Feature
- Keep changes within one service when possible
- If changes span services, that's a contract change — document it
- Run tests frequently: `python -m pytest services/<service>/tests/ -v`
- Logs should appear automatically (shared logger already wired)

### 5. Verify Measurable Outcome
- Run the full test suite: `python -m pytest services/ -v --ignore=services/cv/tests/test_detector.py`
- If frontend: `cd frontend && npm test`
- Check logs for expected behavior
- Verify the metric moved

### 6. Commit with Clear Message
```bash
git add <files>
git commit -m "feat: Add rate limiting to API" -m "- Implement slowapi middleware
- Apply 10 req/min limit to /api/v1/analyze
- Add tests for rate limit behavior
- Tested with dev.ps1"
```

Use conventional commits:
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `test:` — Tests or test fixtures
- `refactor:` — Code refactoring (no behavior change)

### 7. Restart What's Needed
Report what needs restarting:
```
Backend: Restart via Ctrl+C in dev.ps1 terminal (auto-reload will pick up code changes)
Frontend: Restart via Ctrl+C in dev-frontend.ps1 terminal (hot reload will pick up changes)
Neither: Changes don't need restart (documentation, tests)
```

---

## Working on Specific Services

### Adding to API

1. **Define contract** in `contracts/schemas.py`
2. **Write test** in `services/api/tests/test_api.py`
3. **Add endpoint** in `services/api/main.py`
4. **Run tests**: `pytest services/api/tests/ -v`
5. **Commit**: `git commit -m "feat: Add <endpoint>"`
6. **Restart**: `Ctrl+C` in dev terminal, then `.\dev.ps1`

### Adding to Riot Service

1. **Write test** in `services/riot/tests/test_service.py`
2. **Update `service.py`** with new function or modify `get_riot_report()`
3. **Update parser** if new data types added
4. **Run tests**: `pytest services/riot/tests/ -v`
5. **Commit**: `git commit -m "feat: Add <feature> to Riot service"`
6. **No restart needed** (background task, pure function)

### Adding to LLM Service

1. **Write test** in `services/llm/tests/test_coach.py`
2. **Update `coach.py`** with prompt changes or new logic
3. **Run tests**: `pytest services/llm/tests/ -v`
4. **Commit**: `git commit -m "feat: Improve coaching prompt"`
5. **No restart needed** (pure function called by API)

### Adding to Frontend

1. **Write test** in `frontend/__tests__/` (e.g., `page.test.tsx`)
2. **Add component** or update page in `app/` or `components/`
3. **Run tests**: `cd frontend && npm test`
4. **Run dev server**: `.\dev-frontend.ps1`
5. **Commit**: `git commit -m "feat: Add <page or component>"`
6. **Restart**: `Ctrl+C`, then `.\dev-frontend.ps1` (or it auto-reloads)

---

## Common Gotchas

### Services Can't Import Each Other's Code
```python
# ❌ WRONG
from services.riot.service import get_riot_report

# ✅ RIGHT
from contracts.schemas import RiotReport
# ... then use RiotReport type for type hints
```

### Tests Must Be Fast
- Gate tests should run in <2s total for a service
- Mock external APIs (httpx, anthropic)
- Use fixtures for shared setup
- Slow tests go in periodic evals, not gate tests

### Logging Already Wired
```python
from services.logging import get_logger
logger = get_logger(__name__)
logger.info("Event", variable)
```

All services already have this. Just use it.

### Frontend Tests Need Mocks
```typescript
vi.mock('next/navigation', () => ({ useParams: () => ({ id: 'test' }) }))
vi.mocked(fetch).mockResolvedValue(...)
```

### Config via `.env`
Never hardcode secrets. Use `.env` for all config:
```python
import os
api_key = os.getenv("ANTHROPIC_API_KEY", "")
```

---

## Troubleshooting

### Tests fail locally but pass in CI?
- Check Python version: `python --version` (should be 3.10+)
- Ensure venv activated: run `.\dev.ps1` or `. .venv/Scripts/Activate.ps1`
- Check dependencies: `pip install -r requirements.txt`

### Frontend doesn't update when I edit code?
- Check `dev-frontend.ps1` is running (look for "listening on port 3000")
- Hard refresh: `Ctrl+Shift+R` in browser
- Kill and restart: `Ctrl+C`, then `.\dev-frontend.ps1`

### API returns 500 errors?
- Check logs in dev.ps1 terminal
- Verify `.env` has `RIOT_API_KEY` and `ANTHROPIC_API_KEY`
- Verify `DEV_MODE=true` for bypass endpoints
- Run: `python -m pytest services/api/tests/ -v` to debug

### Import errors in Python?
- Check repo root: `cd c:\Users\Edu\Desktop\T\valorant-aim-analyzer`
- Check venv: `. .venv/Scripts/Activate.ps1`
- Reinstall: `pip install -r requirements.txt`
- Check sys.path in code — many services do `sys.path.insert(0, ...)`

---

## Questions?

- Review [CLAUDE.md](CLAUDE.md) first — most questions answered there
- Check relevant service README (e.g., [services/api/README.md](services/api/README.md))
- Review [AGENTS.md](AGENTS.md) for product context
