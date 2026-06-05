# Development startup script — Backend API
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "$root\.venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "ERROR: venv not found at $python" -ForegroundColor Red
    Write-Host "Run: python -m venv .venv && .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Set-Location "$root\services\api"
Write-Host "Starting API on http://localhost:8000 ..." -ForegroundColor Green
& $python -m uvicorn main:app --reload --port 8000
