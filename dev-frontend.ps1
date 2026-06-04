# Development startup script for Valorant Aim Analyzer frontend
# Adds Node.js to PATH and starts the Next.js development server

$env:PATH = "C:\Program Files\nodejs;$env:PATH"
Set-Location "$(Split-Path -Parent $MyInvocation.MyCommand.Path)\frontend"

Write-Host "Starting frontend dev server on port 3000..." -ForegroundColor Green
npm run dev
