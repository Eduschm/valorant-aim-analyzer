# Development Guide

## Quick Start

### Backend API

```powershell
.\dev.ps1
```

Starts the FastAPI server on `http://localhost:8000` with auto-reload.

### Frontend

```powershell
.\dev-frontend.ps1
```

Starts the Next.js dev server on `http://localhost:3000`.

### Full Stack (two terminals)

Terminal 1:
```powershell
.\dev.ps1
```

Terminal 2:
```powershell
.\dev-frontend.ps1
```

## Environment

Both scripts automatically add Node.js (`C:\Program Files\nodejs`) to `$env:PATH` so npm commands work correctly.

If you get permission errors running `.ps1` files, run this once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Testing

### Backend tests
```powershell
cd services
python -m pytest --tb=short -v
```

### Frontend tests
```powershell
cd frontend
npm test
```

## API Endpoints

- `POST /api/v1/analyze` — Submit a Riot ID for analysis
- `GET /api/v1/report/{id}` — Poll for report status
- `GET /api/v1/health` — Health check

## Configuration

Backend config via `.env`:
```
RIOT_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
LOG_LEVEL=INFO
DEV_MODE=true
```

Frontend config via `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MOCK_MODE=false
NEXT_PUBLIC_LOG_LEVEL=debug
```
