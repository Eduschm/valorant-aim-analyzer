---
name: test
description: Run the full test suite for valorant-aim-analyzer — Python backend services and Next.js frontend. Use when asked to run tests, check test status, verify nothing is broken, or before committing. Reports a pass/fail summary with counts and any failures highlighted.
---

Valorant Aim Analyzer: two test lanes — Python (pytest, gate tests for api/riot/llm/cv) and frontend (Vitest). Run from the repo root `valorant-aim-analyzer/`.

## Prerequisites

- Python venv at `.venv/` activated (`pip install -r requirements.txt`)
- Node deps installed (`cd frontend && npm install`)

## What this runs

| Suite | Command | Notes |
|---|---|---|
| Python – all services | `python -m pytest services/ -v --ignore=services/cv/tests/test_detector.py` | Skips CV detector which needs ultralytics GPU setup |
| Frontend | `cd frontend && npm test -- --run` | Vitest in single-run mode (no watch) |

## Agent instructions

1. Verify you're in the repo root: `valorant-aim-analyzer/` (the directory containing `services/`, `frontend/`, `pytest.ini`).
2. Activate venv if not already: `.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (Linux/Mac).
3. Run Python tests first (faster, gate tests):
   ```powershell
   python -m pytest services/ -v --ignore=services/cv/tests/test_detector.py
   ```
4. Run frontend tests:
   ```powershell
   cd frontend; npm test -- --run; cd ..
   ```
5. Report results as a table:
   | Suite | Result | Passed | Failed | Skipped |
   |---|---|---|---|---|
   | Python | PASS/FAIL | N | N | N |
   | Frontend | PASS/FAIL | N | N | N |
6. If any tests fail, quote the exact failure message and file:line so the fix is unambiguous.
7. Known pre-existing failure: `frontend/app/analysis/[id]/__tests__/page.test.tsx` may fail with a RolldownError parse failure — check if this was pre-existing on `main` before assuming your change caused it.

## Pass threshold

- Python: 0 failures (all gate tests must pass)
- Frontend: 0 failures outside the known pre-existing `page.test.tsx` parse issue

## Running a single service

```powershell
python -m pytest services/api/tests/ -v
python -m pytest services/riot/tests/ -v
python -m pytest services/llm/tests/ -v
python -m pytest services/cv/tests/ -v --ignore=services/cv/tests/test_detector.py
```
