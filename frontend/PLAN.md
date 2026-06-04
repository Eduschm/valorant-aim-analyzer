# Frontend Implementation Plan
## Valorant Aim Analyzer — Phase 1 (Tracker-only MVP)

This document is the complete spec for a separate agent to implement.
Do not deviate from decisions marked ✅. Confusion Protocol applies to anything ambiguous.

---

## Stack

| Layer | Choice | Reason |
|---|---|---|
| Framework | Next.js 14 (App Router) | SSR for report pages, easy Vercel deploy |
| Styling | Tailwind CSS | Fast, no design system overhead |
| Components | shadcn/ui | Accessible, unstyled-by-default, copy-paste |
| State | React built-ins (useState/useContext) | No Redux — MVP has no complex shared state |
| HTTP | fetch (native) | No axios — keep it vanilla |
| Auth | Magic link email (Resend) | No passwords, Riot ID = account identity |
| Forms | react-hook-form + zod | Validation without ceremony |

---

## Directory structure

```
frontend/
├── app/
│   ├── layout.tsx               # root layout, font, metadata
│   ├── page.tsx                 # landing page
│   ├── analyze/
│   │   └── page.tsx             # Riot ID input + submit form
│   ├── report/
│   │   └── [id]/
│   │       └── page.tsx         # analysis results page
│   ├── dashboard/
│   │   └── page.tsx             # user history (paid tier, future)
│   └── api/
│       ├── analyze/route.ts     # POST: submit analysis request
│       └── report/[id]/route.ts # GET: fetch report status + data
├── components/
│   ├── ui/                      # shadcn components (Button, Card, etc.)
│   ├── RiotIdForm.tsx           # main input form
│   ├── ReportCard.tsx           # single mistake breakdown card
│   ├── MistakeChart.tsx         # bar chart of mistake impact scores
│   ├── DetectionStats.tsx       # enemies/allies detected breakdown
│   ├── CoachingTips.tsx         # LLM coaching output
│   └── LoadingState.tsx         # polling skeleton while report processes
├── lib/
│   ├── api.ts                   # typed fetch wrappers for /api routes
│   └── types.ts                 # TypeScript types mirroring contracts/schemas.py
├── public/
│   └── valorant-bg.jpg          # dark background image (source separately)
└── tailwind.config.ts
```

---

## Pages

### 1. Landing (`/`)

**Goal:** communicate value, drive to `/analyze`.

Layout:
- Full-bleed dark background (Valorant aesthetic — dark navy/charcoal)
- Hero: large headline + 1-line subheadline + single CTA button
- 3 feature columns below: "Detect mistakes", "Riot stats", "AI coaching"
- No navbar needed for MVP

Copy (exact):
- Headline: `Stop guessing why you lose gunfights.`
- Subheadline: `Paste your Riot ID. Get a personalised aim analysis in 30 seconds.`
- CTA: `Analyze my aim →`

### 2. Analyze (`/analyze`)

Single form:
```
┌─────────────────────────────────────────┐
│  Enter your Riot ID                      │
│  ┌──────────────────────┐               │
│  │  PlayerName#NA1       │               │
│  └──────────────────────┘               │
│                                          │
│  [ Analyze my aim → ]                   │
│                                          │
│  No account needed. Free.               │
└─────────────────────────────────────────┘
```

Validation (zod):
- Must match pattern: `\w+#\w+` (name + # + tag)
- Error: "Format: PlayerName#TAG (e.g. Shroud#1234)"

On submit:
1. POST `/api/analyze` with `{ riot_id }`
2. Redirect to `/report/[id]` with the returned report ID

### 3. Report (`/report/[id]`)

Polls `GET /api/report/[id]` every 3 seconds until `status === "done"`.

While processing: show `LoadingState` (skeleton cards + spinner + "Fetching your last 20 matches...")

When done, render in this order:

```
┌──────────────────────────────────────────────┐
│  PlayerName#NA1 — Iron 2                     │
│  Win rate 48%  •  Avg HS% 18%  •  ADR 142   │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│  AI Coaching                                  │
│  [CoachingTips component]                    │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│  Mistake Breakdown  [MistakeChart]           │
│  [ReportCard × N mistakes]                   │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│  Detection Stats  [DetectionStats]           │
│  Enemies seen: 47  •  Head-level: 31%        │
└──────────────────────────────────────────────┘
```

---

## Components

### `RiotIdForm`
- Input + submit button
- Controlled with react-hook-form
- Shows inline zod validation error
- Button shows spinner while POST is in-flight
- On error from API: show error toast (shadcn Toast)

### `MistakeChart`
- Horizontal bar chart of `impact_scores` from CV report
- Each bar: mistake label on left, impact score bar, % share on right
- Colour-coded per mistake type (match `config.MISTAKE_COLORS` in services/cv)
- Use plain SVG or CSS bars — no chart library for MVP

### `ReportCard`
- One card per mistake type that has count > 0
- Shows: icon, label, count, avg severity (0-1 → Low/Med/High), description of worst instance

### `DetectionStats`
- Grid of stats pills: enemies seen, allies seen, head detections, frames with enemy visible
- Only shown when CV report is present (Phase 2); hide gracefully if `cv_report === null`

### `CoachingTips`
- Shows `coaching.summary` in larger text
- Shows `coaching.top_weakness` as a highlighted callout
- Shows `coaching.tips` as a numbered list
- Shows `coaching.encouragement` in italic at the bottom

### `LoadingState`
- Skeleton version of the report layout
- Status text that cycles: "Fetching match history..." → "Analysing stats..." → "Generating report..."
- Cycle every 4 seconds using setInterval

---

## API routes

### `POST /api/analyze`

Request body: `{ riot_id: string }`

Response:
```json
{ "report_id": "abc123", "status": "processing" }
```

Internally: calls `services/api` backend (URL from `NEXT_PUBLIC_API_URL` env var).
If backend is not yet running, return a **mock response** for now:
```json
{ "report_id": "mock-001", "status": "done" }
```

### `GET /api/report/[id]`

Response when done:
```json
{
  "status": "done",
  "riot_report": { ... },
  "cv_report": null,
  "coaching": { ... }
}
```

For mock mode, return hardcoded fixture data from `lib/fixtures.ts`.

---

## Mock fixtures (`lib/fixtures.ts`)

The backend does not exist yet. The frontend must work end-to-end with mock data.
Create realistic fixture data matching the contract types:

```typescript
export const MOCK_REPORT = {
  status: "done",
  riot_report: {
    game_name: "DemoPlayer",
    tag_line: "NA1",
    current_rank: "Iron 2",
    rank_delta: -1,
    avg_headshot_pct: 18.4,
    avg_adr: 142.3,
    win_rate: 0.48,
    top_agent: "Jett",
    top_weapon: "Vandal",
    matches: []
  },
  cv_report: null,    // Phase 2
  coaching: {
    summary: "Your headshot percentage is below average for your rank. You're winning most duels you enter but losing the ones that matter — likely due to inconsistent crosshair placement.",
    top_weakness: "Low headshot rate (18% vs 25% average for Iron 2)",
    tips: [
      "Keep your crosshair at head height when pre-aiming corners — most deaths come from looking at the floor.",
      "On pistol rounds, switch to Ghost instead of Classic. Your ADR suggests you can win duels but need the extra accuracy.",
      "Review your last 3 losses — your win rate drops on Bind specifically, likely a map positioning issue."
    ],
    encouragement: "You have the right instincts — just sharpen the fundamentals and the rank will follow."
  }
}
```

---

## Environment variables

```
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000   # points to FastAPI backend
NEXT_PUBLIC_MOCK_MODE=true                 # set true to use fixtures, false for real API
```

---

## Design tokens (Tailwind)

```
Background:  #0F1117  (near-black)
Surface:     #1A1D27  (card backgrounds)
Border:      #2A2D3A
Primary:     #FF4655  (Valorant red)
Text:        #E8E8E8  (primary)
Muted:       #8B8FA8  (secondary text)
Success:     #22C55E
Warning:     #F59E0B
Danger:      #EF4444
```

Font: `Inter` (Google Fonts, next/font)

---

## Setup commands

```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"
npx shadcn@latest init
npx shadcn@latest add button card input toast badge skeleton
npm install react-hook-form zod @hookform/resolvers
```

---

## Acceptance criteria

The agent is DONE when:
1. `npm run dev` starts with no errors
2. `/` renders the landing page
3. `/analyze` renders the form; submitting `Demo#NA1` navigates to `/report/mock-001`
4. `/report/mock-001` shows the full mock report with all components rendered
5. `LoadingState` is visible for ~2s before mock data appears (simulate with setTimeout)
6. TypeScript compiles with no errors (`npm run build`)
7. Mobile layout works at 375px width (Tailwind responsive classes)

---

## Out of scope for this task

- Auth / magic link
- Real API integration (backend doesn't exist yet)
- Payments / Stripe
- Dashboard / history
- Video upload UI
- Dark/light mode toggle
