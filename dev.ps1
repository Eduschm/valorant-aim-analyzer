# Development startup script for Valorant Aim Analyzer
# Adds Node.js to PATH and starts the backend API server

$env:PATH = "C:\Program Files\nodejs;$env:PATH"
Set-Location "$(Split-Path -Parent $MyInvocation.MyCommand.Path)\services\api"

Write-Host "Starting API server on port 8000..." -ForegroundColor Green
python -m uvicorn main:app --reload --port 8000
