# Development startup script — Frontend
$root  = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PATH = "C:\Program Files\nodejs;$env:PATH"

Set-Location "$root\frontend"

# Clear stale Next.js cache (prevents old pages showing up)
if (Test-Path ".next") {
    Remove-Item -Recurse -Force ".next"
    Write-Host "Cleared .next cache" -ForegroundColor Yellow
}

Write-Host "Starting frontend on http://localhost:3000 ..." -ForegroundColor Green
npm run dev
