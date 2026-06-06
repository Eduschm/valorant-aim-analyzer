---
name: env-check
description: Validate the local environment for valorant-aim-analyzer before starting a dev session — checks .env keys, venv, Node, ports. Use when starting work, after a fresh clone, or when hitting mysterious runtime errors.
---

Validates everything needed to run valorant-aim-analyzer locally. Reports each check as PASS/FAIL/WARN with a fix for each failure.

## What it checks

| Check | Pass condition | Fix if fail |
|---|---|---|
| `.env` file exists | File present at repo root | Copy `.env.example` → `.env` and fill keys |
| `RIOT_API_KEY` set | Non-empty, starts with `RGAPI-` | Get dev key at https://developer.riotgames.com (expires 24h) |
| `HENRIK_API_KEY` set | Non-empty, starts with `HDEV-` | HenrikDev Discord → #get-a-key (free). Without it, match data falls back to Riot's val/match/v1 which 403s on dev keys — every analysis will error. |
| `ANTHROPIC_API_KEY` set | Non-empty, starts with `sk-ant-` | Get at https://console.anthropic.com |
| `DEV_MODE` set | Value is `true` | Add `DEV_MODE=true` to `.env` for local dev |
| Python venv exists | `.venv/` directory present | `python -m venv .venv` |
| Python deps installed | `import fastapi` succeeds | `.venv\Scripts\pip install -r requirements.txt` |
| Node installed | `node --version` returns 18+ | Install Node 18+ from nodejs.org |
| Frontend deps installed | `frontend/node_modules/` exists | `cd frontend && npm install` |
| Port 8000 free | No process on 8000 | `netstat -ano \| findstr :8000` then `taskkill /PID <pid> /F` |
| Port 3000 free | No process on 3000 | `netstat -ano \| findstr :3000` then `taskkill /PID <pid> /F` |
| `frontend/.env.local` exists | File present | Create with `NEXT_PUBLIC_API_URL=http://localhost:8000` and `NEXT_PUBLIC_MOCK_MODE=false` |

## Agent instructions

Run each check in order. Use PowerShell on Windows.

```powershell
# 1. .env exists
Test-Path ".env"

# 2+3+4. Parse .env for required keys
$env_content = Get-Content ".env" -Raw -ErrorAction SilentlyContinue
$riot_key = if ($env_content -match 'RIOT_API_KEY=(.+)') { $matches[1].Trim() } else { "" }
$anthropic_key = if ($env_content -match 'ANTHROPIC_API_KEY=(.+)') { $matches[1].Trim() } else { "" }
$henrik_key = if ($env_content -match 'HENRIK_API_KEY=(.+)') { $matches[1].Trim() } else { "" }
$dev_mode = if ($env_content -match 'DEV_MODE=(.+)') { $matches[1].Trim() } else { "" }
Write-Host "RIOT_API_KEY: $(if ($riot_key -and $riot_key -ne 'RGAPI-...') { 'SET' } else { 'MISSING or placeholder' })"
Write-Host "HENRIK_API_KEY: $(if ($henrik_key -and $henrik_key -ne 'HDEV-xxxxx') { 'SET' } else { 'MISSING — analyses will error without this' })"
Write-Host "ANTHROPIC_API_KEY: $(if ($anthropic_key -and $anthropic_key -ne 'sk-ant-...') { 'SET' } else { 'MISSING or placeholder' })"
Write-Host "DEV_MODE: $dev_mode"

# 5. Venv
Test-Path ".venv"

# 6. Python deps (fast import check)
if (Test-Path ".venv\Scripts\python.exe") {
    .venv\Scripts\python.exe -c "import fastapi, uvicorn, httpx, anthropic" 2>&1
}

# 7. Node
node --version 2>&1

# 8. Frontend deps
Test-Path "frontend\node_modules"

# 9+10. Ports
$p8000 = netstat -ano 2>&1 | Select-String ":8000 "
$p3000 = netstat -ano 2>&1 | Select-String ":3000 "
Write-Host "Port 8000: $(if ($p8000) { 'IN USE' } else { 'FREE' })"
Write-Host "Port 3000: $(if ($p3000) { 'IN USE' } else { 'FREE' })"

# 11. frontend/.env.local
Test-Path "frontend\.env.local"
```

## Report format

Print a table:

```
ENV CHECK — valorant-aim-analyzer
==================================
.env file          PASS
RIOT_API_KEY       PASS  (RGAPI-xxxxx...)
ANTHROPIC_API_KEY  WARN  (placeholder — real Riot data won't work)
DEV_MODE           PASS  (true)
Python venv        PASS
Python deps        PASS
Node 18+           PASS  (v20.11.0)
Frontend deps      PASS
Port 8000          FREE
Port 3000          FREE
frontend/.env.local  PASS
----------------------------------
STATUS: READY (1 warning)
```

Statuses: **PASS** = green, **WARN** = yellow (app runs but feature degraded), **FAIL** = red (app won't start).

Any FAIL = stop and fix before proceeding.

## Common WARN cases

- `RIOT_API_KEY` = placeholder → analysis pipeline returns errors, dev bypass still works
- `ANTHROPIC_API_KEY` = placeholder → coaching report fails, rest of app works
- `frontend/.env.local` missing → frontend defaults to mock mode (may cause confusion)
