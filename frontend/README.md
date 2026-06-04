# Frontend

Next.js/React web app for Valorant Aim Analyzer. Calls the API backend.

## Quick Start

```bash
cd frontend
npm install
npm run dev
```

Starts dev server on `http://localhost:3000`.

Or from repo root:
```bash
.\dev-frontend.ps1  # PowerShell
```

## Architecture

- **Framework**: Next.js 14+ with App Router
- **Styling**: Tailwind CSS
- **State**: Zustand (lib/store.ts)
- **Testing**: Vitest + React Testing Library
- **HTTP**: Native fetch with logger (lib/api.ts)

## Directory Structure

```
app/                    # Next.js app routes
├── analysis/
│   ├── new/           # Input form (Riot ID)
│   └── [id]/          # Report page (polling)
├── auth/
│   └── signin/        # Magic link form
├── dashboard/         # Analysis history
├── profile/           # User stats
├── settings/          # Config
├── tracker/           # Rank trends
└── layout.tsx         # Root layout

components/            # Reusable React components
├── analysis/
├── auth/
├── dashboard/
├── layout/
├── profile/
├── tracker/
└── ...

lib/                   # Utilities
├── api.ts             # HTTP client
├── logger.ts          # Logging
├── storage.ts         # localStorage persistence
├── store.ts           # Zustand state
├── hooks.ts           # Custom React hooks
├── constants.ts       # Magic strings
├── types.ts           # TypeScript types
└── mock/              # Mock data for development

__tests__/             # Component tests
```

## Pages

| Path | Purpose |
|------|---------|
| `/` | Landing page |
| `/analysis/new` | Submit Riot ID |
| `/analysis/[id]` | View report (polling) |
| `/dashboard` | Analysis history |
| `/profile` | User profile |
| `/tracker` | Rank trends |
| `/settings` | Configuration |
| `/auth/signin` | Sign in |

## State Management

### `lib/store.ts` (Zustand)

```javascript
const { user, analyses, setUser, saveAnalysis } = useAuthStore()
```

Persists to localStorage automatically.

### `lib/storage.ts`

```javascript
saveAnalysis(report)          // Save to localStorage
getAllAnalyses()              // Get all analyses
getAnalyses(riotId)          // Get analyses for Riot ID
clearAnalyses()               // Clear all (sign out)
```

## Environment

### `.env.local`

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MOCK_MODE=false
NEXT_PUBLIC_LOG_LEVEL=debug
```

### Development

- `NEXT_PUBLIC_MOCK_MODE=true` — Use mock data, no API calls
- `NEXT_PUBLIC_LOG_LEVEL=debug` — Show all logs
- Auto-reload on file changes

### Production

- `NEXT_PUBLIC_MOCK_MODE=false` — Use real API
- `NEXT_PUBLIC_LOG_LEVEL=info` — Only info and errors
- Build optimization enabled

## API Integration

### `lib/api.ts`

```javascript
// Typed HTTP client with logging
async function request<T>(endpoint, options)

// Analysis endpoints
async function submitAnalysis(riotId)
async function getReport(reportId)
```

Logs all requests/responses (controlled by `NEXT_PUBLIC_LOG_LEVEL`).

## Testing

```bash
npm test                  # Run all tests
npm run test:watch       # Watch mode
npm run test:coverage    # Coverage report
```

Tests use Vitest + React Testing Library. Mock `fetch` and `next/navigation`.

## Building

```bash
npm run build            # Production build
npm run start            # Run production build locally
npm run lint             # Run ESLint
```

## Logging

### `lib/logger.ts`

```javascript
import { logger } from '@/lib/logger'

logger.debug('Message', arg1, arg2)
logger.info('Info')
logger.warn('Warning')
logger.error('Error')
```

Levels:
- `debug` (10)
- `info` (20)
- `warn` (30)
- `error` (40)

Controlled by `NEXT_PUBLIC_LOG_LEVEL`. Default: `debug` in dev, `info` in prod.

## Notes

- **No passwords**: Magic link auth only
- **localStorage persistence**: Analyses saved locally after completion
- **Offline-friendly**: Reports stay accessible even if API is down
- **Mock mode**: Useful for frontend development without API
