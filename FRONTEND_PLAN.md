# Valorant Aim Analyzer — Frontend Development Plan

## Overview
This plan outlines the frontend development for the Valorant Aim Analysis SaaS. The frontend will be built with Next.js (React) and deployed on Vercel, following a phased approach aligned with the overall project timeline.

---

## Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | Next.js 14 (App Router) | SEO-friendly, server components, API routes, easy Vercel deployment |
| UI Library | shadcn/ui | Modern, customizable components built on Radix UI + Tailwind |
| Styling | Tailwind CSS | Utility-first, fast development, small bundle |
| State Management | React Context + Zustand | Simple state for auth, complex state for analysis results |
| Forms | React Hook Form + Zod | Type-safe validation, great DX |
| HTTP Client | fetch + SWR or TanStack Query | Built-in fetch, SWR for data fetching/caching |
| Auth | NextAuth.js (v5) | Magic link email auth, Riot ID linking |
| Icons | Lucide React | Lightweight, tree-shakeable |
| Charts | Recharts | Simple, responsive charts for progress tracking |
| Video Player | react-player or Video.js | Clip playback with annotations |
| Deployment | Vercel | Zero-config deployment, preview deployments |

---

## Phase 1: Tracker-Only MVP Frontend (Weeks 1–2)

### Core Features
- Landing page with value proposition
- Magic link email authentication
- Riot ID linking form
- Simple analysis request form (Riot ID only)
- Report display page
- User dashboard (analysis history)

### Page Structure

```
/                           → Landing page
/auth/signin                → Magic link auth
/auth/callback              → OAuth callback
/auth/link-riot-id          → Riot ID linking
/dashboard                  → User dashboard
/analysis/new               → New analysis form (tracker-only)
/analysis/[id]              → Analysis report view
/settings                   → Account settings
```

### Component Architecture

```
components/
├── layout/
│   ├── Header.tsx          → Navigation, auth state
│   ├── Footer.tsx          → Links, branding
│   └── Sidebar.tsx         → Dashboard navigation
├── auth/
│   ├── MagicLinkForm.tsx   → Email input for magic link
│   ├── RiotIdLinkForm.tsx  → Riot ID + tagline input
│   └── AuthGuard.tsx       → Route protection wrapper
├── analysis/
│   ├── AnalysisForm.tsx    → Riot ID input, submit button
│   ├── ReportView.tsx      → Claude-generated report display
│   ├── StatsCards.tsx      → HS%, ADR, rank delta cards
│   └── WeaponStats.tsx     → Weapon distribution chart
├── dashboard/
│   ├── AnalysisHistory.tsx → List of past analyses
│   ├── QuickStats.tsx      → Recent performance summary
│   └── UsageMeter.tsx      → Free tier usage (placeholder)
└── ui/                     → shadcn/ui components
```

### Key Flows

#### 1. Authentication Flow
```
User visits /dashboard
    ↓
Not authenticated → redirect to /auth/signin
    ↓
Enter email → send magic link
    ↓
Click email link → /auth/callback → create session
    ↓
Redirect to /auth/link-riot-id
    ↓
Enter Riot ID + tagline (e.g., "Edu#1234")
    ↓
Validate via Riot API → link to account
    ↓
Redirect to /dashboard
```

#### 2. Analysis Request Flow (Phase 1)
```
User clicks "New Analysis" on dashboard
    ↓
Navigate to /analysis/new
    ↓
Enter Riot ID (pre-filled if linked)
    ↓
Submit → POST to /api/analysis/tracker
    ↓
Show loading state with skeleton UI
    ↓
Poll for completion (or WebSocket)
    ↓
Redirect to /analysis/[id] when ready
```

#### 3. Report Display Flow
```
Navigate to /analysis/[id]
    ↓
Fetch analysis data from API
    ↓
Display:
  - Match summary (last 20 matches)
  - Key stats cards (HS%, ADR, rank change)
  - Weapon usage chart
  - Agent performance table
  - Claude-generated coaching tips (markdown)
  - Weakness identification
    ↓
"Share" button (copy link)
"Download PDF" (optional, Phase 3)
```

### Design System

#### Color Palette (Valorant-inspired)
```css
--primary: #FF4655;      /* Valorant red */
--primary-dark: #C4323E;
--secondary: #0F1923;    /* Dark background */
--accent: #69C9D0;       /* Cyan accent */
--text-primary: #ECE8E1;
--text-secondary: #8B9BB4;
--surface: #1F2731;
--surface-hover: #2A3542;
```

#### Typography
- Headings: Inter or Rajdhani (gaming feel)
- Body: Inter
- Monospace: JetBrains Mono for stats/IDs

### API Integration Points

#### Phase 1 Endpoints
```typescript
// Authentication
POST /api/auth/signin          → Send magic link
GET  /api/auth/session         → Get current session
POST /api/auth/link-riot-id    → Link Riot ID to account

// Analysis
POST /api/analysis/tracker     → Request tracker-only analysis
GET  /api/analysis/[id]        → Get analysis result
GET  /api/analysis/history     → Get user's analysis history

// User
GET  /api/user/profile         → Get user profile (Riot ID, usage)
PUT  /api/user/profile         → Update profile
```

### Mock Data for Development
Create mock analysis responses to develop UI before backend is ready:
```typescript
// mock/analysis.ts
export const mockAnalysis = {
  id: "analysis_123",
  riotId: "Edu#1234",
  createdAt: "2024-06-04T12:00:00Z",
  status: "completed",
  stats: {
    headshotPercent: 42.5,
    adr: 156.8,
    rankDelta: "+12 RR",
    matchesAnalyzed: 20,
  },
  weaponStats: [
    { weapon: "Vandal", kills: 145, accuracy: 22.4 },
    { weapon: "Phantom", kills: 89, accuracy: 19.8 },
    // ...
  ],
  agentStats: [
    { agent: "Jett", matches: 8, winRate: 62.5 },
    // ...
  ],
  coachingReport: `
# Your Aim Analysis

## Strengths
- Strong crosshair placement on entry
- Consistent first-shot accuracy

## Weaknesses
- Slow target acquisition on wide swings
- Over-aiming on close-range fights

## Recommendations
1. Practice wide-swing tracking in The Range
2. Reduce sensitivity by 5-10%
3. Focus on pre-aiming common angles
  `,
};
```

---

## Phase 2: Add Clip Analysis Frontend (Weeks 3–6)

### New Features
- Video upload interface (drag & drop)
- Upload progress indicator
- Clip duration validation (3 min max for free tier)
- Processing status with queue position
- Annotated video player
- Engagement timeline visualization
- Combined tracker + clip report

### New Pages
```
/analysis/new-clip           → Clip upload form
/analysis/[id]/video         → Video player with annotations
/analysis/[id]/timeline      → Engagement timeline view
```

### New Components

```
components/
├── upload/
│   ├── ClipUploader.tsx      → Drag & drop, file picker
│   ├── UploadProgress.tsx    → Progress bar, queue position
│   ├── DurationValidator.tsx → Check 3 min limit
│   └── FormatInfo.tsx        → Supported formats info
├── video/
│   ├── AnnotatedPlayer.tsx   → Video player with overlay
│   ├── FrameViewer.tsx       → Scrollable frame gallery
│   ├── EngagementMarker.tsx  → Timeline markers
│   └── PlaybackControls.tsx  → Custom controls
├── timeline/
│   ├── EngagementTimeline.tsx → Visual timeline of engagements
│   ├── OffsetChart.tsx       → Screen-center offset over time
│   └── Heatmap.tsx           → Miss pattern visualization
└── analysis/
    ├── ClipMetrics.tsx       → Clip-specific metrics
    └── CombinedReport.tsx    → Tracker + clip synthesis
```

### Clip Upload Flow
```
User navigates to /analysis/new-clip
    ↓
Drag & drop video file OR click to browse
    ↓
Validate:
  - File type (MP4, WebM, MOV)
  - Duration (≤ 3 min for free tier)
  - File size (≤ 500MB)
    ↓
Show preview with duration
    ↓
Enter optional context (map, agent, round)
    ↓
Submit → POST /api/analysis/clip
    ↓
Upload to S3/R2 (presigned URL)
    ↓
Redirect to /analysis/[id] with status="processing"
    ↓
Poll for completion every 5s
    ↓
Show queue position if queued
    ↓
When complete → redirect to /analysis/[id]/video
```

### Annotated Video Player
```typescript
// Features needed:
- Video playback with frame-by-frame
- Overlay showing:
  - Screen center (crosshair)
  - Detected enemy head positions (bounding boxes)
  - Offset distance visualization
- Timeline with engagement markers
- Click marker to jump to timestamp
- Keyboard shortcuts (space, arrows, frame-by-frame)
- Export annotated frames as images
```

### Engagement Timeline UI
```
Timeline bar (0:00 to 3:00)
    ↓
Markers for each engagement:
  - Green: Good aim (offset < threshold)
  - Yellow: Moderate aim
  - Red: Poor aim (offset > threshold)
    ↓
Click marker → jump to video timestamp
    ↓
Show metrics for that engagement:
  - Offset distance (pixels)
  - Reaction time (ms)
  - Pre-aim accuracy
```

### New API Endpoints (Phase 2)
```typescript
POST /api/analysis/clip              → Upload clip + request analysis
POST /api/upload/presigned-url        → Get S3/R2 upload URL
GET  /api/analysis/[id]/frames       → Get annotated frames
GET  /api/analysis/[id]/engagements   → Get engagement data
GET  /api/analysis/[id]/video-url     → Get processed video URL
```

---

## Phase 3: Monetization & Launch Frontend (Weeks 7–12)

### New Features
- Stripe checkout integration
- Credit-based usage display
- Pricing page
- Progress tracking dashboard
- 7-day trial flow
- Usage analytics
- Refund request form

### New Pages
```
/pricing                    → Pricing tiers
/checkout                   → Stripe checkout
/billing                    → Billing history, manage subscription
/progress                   → Long-term progress tracking
/settings/billing           → Payment method, plan management
/refund-request             → Refund request form
```

### New Components

```
components/
├── billing/
│   ├── PricingCard.tsx     → Free vs Paid tier comparison
│   ├── UsageMeter.tsx      → Credits used / total
│   ├── CreditDisplay.tsx   → Remaining credits
│   └── BillingHistory.tsx  → Invoice list
├── progress/
│   ├── ProgressChart.tsx    → HS% over time
│   ├── RankTrajectory.tsx   → Rank history chart
│   ├── StreakCalendar.tsx  → Analysis streak visualization
│   └── MilestoneCard.tsx   → Achievement milestones
├── checkout/
│   ├── TrialBanner.tsx     → 7-day trial CTA
│   ├── UpgradeModal.tsx    → Upgrade prompt
│   └── PaymentForm.tsx     → Stripe Elements
└── settings/
    ├── PlanSwitcher.tsx    → Change plan
    └── CancelSubscription.tsx → Cancel flow
```

### Pricing Page Design
```
Hero: "Unlock Your Full Potential"

Two cards side by side:

FREE TIER                          PAID TIER
$0/month                          $9/month
• 10 clips/month                  • 40 clips/month
• 3 min max clip length           • Unlimited clip length
• Basic tracker analysis          • Full tracker history
• Basic report                    • Progress tracking
•                                  • Priority processing
•                                  • Advanced metrics

CTA: "Start Free"                 CTA: "Start 7-Day Trial"
```

### Usage Meter UI
```
Dashboard header:
┌─────────────────────────────────────┐
│ Credits: 7/10 remaining             │
│ ████████░░ 70% used                 │
│ Resets in 5 days                    │
└─────────────────────────────────────┘

Upgrade button → /pricing
```

### Progress Tracking Dashboard (Paid Tier)
```
/time-series charts:
- Headshot % over last 30 analyses
- ADR trend line
- Rank trajectory (RR over time)

/stat cards:
- Current rank
- Best performing agent
- Most used weapon
- Analysis streak (days)

/engagement heatmap:
- Heatmap of miss patterns
- Improvement areas highlighted

/milestones:
- "First 50% HS match" ✓
- "10 analysis streak" ✓
- "Diamond rank reached" ○
```

### Stripe Integration Flow
```
User clicks "Upgrade" or "Start Trial"
    ↓
Navigate to /checkout
    ↓
Display plan summary
    ↓
Create Stripe Checkout Session via API
    ↓
Redirect to Stripe hosted checkout
    ↓
User completes payment (or $0 hold for trial)
    ↓
Stripe webhook → update user subscription in DB
    ↓
Redirect to /billing with success message
```

### New API Endpoints (Phase 3)
```typescript
POST /api/checkout/create-session    → Create Stripe session
POST /api/webhook/stripe             → Stripe webhook handler
GET  /api/user/subscription          → Get current subscription
GET  /api/user/usage                 → Get credit usage
GET  /api/progress/history           → Get progress data
POST /api/refund/request             → Submit refund request
```

---

## Responsive Design Strategy

### Breakpoints
```css
/* Mobile First */
sm: 640px   /* Large phones */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large screens */
```

### Mobile Considerations
- Stack layouts on mobile
- Touch-friendly video controls
- Simplified dashboard (hide advanced charts)
- Bottom navigation for mobile (optional)
- Optimize video upload for mobile (compress client-side)

---

## Performance Optimizations

### Image/Video Optimization
- Use Next.js Image component for static assets
- Lazy load annotated frames
- Video thumbnails as WebP
- Progressive video loading

### Code Splitting
- Route-based splitting (automatic in Next.js)
- Dynamic imports for heavy components (charts, video player)
- Separate analytics bundle

### Caching Strategy
- SWR for analysis data (revalidate on focus)
- Cache user profile for 5 min
- Cache static report data
- Invalidate cache on new analysis

---

## Accessibility

### WCAG 2.1 AA Compliance
- Semantic HTML
- ARIA labels for custom components
- Keyboard navigation for video player
- Color contrast ratios (4.5:1 minimum)
- Focus indicators
- Screen reader support for charts

### Key Accessibility Features
- Skip to main content link
- Alt text for annotated frames
- Video captions (optional, user-generated)
- High contrast mode toggle
- Reduced motion support

---

## Internationalization (Future)

### Planned Support
- English (primary)
- Portuguese (Brazil) - large Valorant market
- Spanish (LatAm)

### Implementation
- Use next-intl or next-i18next
- Separate locale routes (/en, /pt-BR, /es)
- Currency localization (BRL for Brazil)
- Riot ID format validation per region

---

## Development Workflow

### Local Development Setup
```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Run on http://localhost:3000

# Type checking
npm run type-check

# Linting
npm run lint

# Format
npm run format
```

### Environment Variables
```env
# .env.local
NEXTAUTH_SECRET=your-secret
NEXTAUTH_URL=http://localhost:3000
RIOT_API_KEY=your-riot-key
ANTHROPIC_API_KEY=your-claude-key
STRIPE_SECRET_KEY=your-stripe-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
DATABASE_URL=your-db-url
```

### Git Workflow
- Feature branches: `feature/clip-upload`, `feature/pricing-page`
- PR required for main branch
- Automated tests on PR
- Deploy preview on Vercel for each PR

---

## Testing Strategy

### Unit Tests
- Component rendering with React Testing Library
- Form validation logic
- Utility functions
- Hook behavior

### Integration Tests
- Authentication flow
- Analysis submission flow
- Video upload flow
- Checkout flow

### E2E Tests (Playwright)
- Critical user journeys:
  1. Sign up → link Riot ID → request analysis
  2. Upload clip → view annotated video
  3. Upgrade to paid → view progress dashboard

### Visual Regression
- Chromatic or Percy for component screenshots
- Catch UI changes across updates

---

## Deployment

### Vercel Configuration
```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXTAUTH_SECRET": "@nextauth-secret",
    "RIOT_API_KEY": "@riot-api-key"
  }
}
```

### Deployment Checklist
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Stripe webhooks configured
- [ ] CDN cache purged
- [ ] Analytics tracking installed
- [ ] Error monitoring (Sentry) setup

---

## Analytics & Monitoring

### Tools
- Vercel Analytics (built-in)
- PostHog or Plausible (user analytics)
- Sentry (error tracking)
- LogRocket (session replay for debugging)

### Key Metrics to Track
- Sign-up conversion rate
- Analysis completion rate
- Clip upload success rate
- Free to paid conversion
- Churn rate
- Video processing time
- Page load times

---

## Security Considerations

### Frontend Security
- CSP headers configured
- XSS protection (React auto-escapes)
- CSRF protection (NextAuth handles)
- Rate limiting on API routes
- Input validation on all forms
- Secure file upload validation

### Data Privacy
- No PII in URLs
- Encrypt Riot IDs in DB
- Delete clips after processing
- GDPR compliance (data export/delete)
- Clear privacy policy

---

## Launch Checklist

### Pre-Launch
- [ ] All Phase 1 features tested
- [ ] Phase 2 features tested (if launching with clips)
- [ ] Phase 3 billing tested
- [ ] Error pages (404, 500) designed
- [ ] Loading states for all async operations
- [ ] Mobile responsive on all pages
- [ ] Accessibility audit passed
- [ ] Performance audit (Lighthouse > 90)

### Launch Day
- [ ] DNS configured
- [ ] SSL certificate valid
- [ ] Monitoring alerts set up
- [ ] Backup plan documented
- [ ] Support email ready
- [ ] Social media accounts linked

### Post-Launch
- [ ] Monitor error rates
- [ ] Track user feedback
- [ ] A/B test pricing page
- [ ] Optimize video processing queue
- [ ] Add FAQ based on user questions

---

## Out of Scope (Explicitly Deferred)

These features are NOT in the frontend plan for first 3 months:
- Desktop client UI
- Mobile app (React Native)
- Discord bot UI
- Live coaching interface
- Multi-game support (CS2, Apex)
- Team/coach dashboard
- Replay file viewer
- Custom drill builder UI

---

## Success Metrics for Frontend

### Phase 1 Success
- [ ] 20+ test users complete tracker analysis
- [ ] Average time from sign-up to first analysis < 5 min
- [ ] Report page load time < 2s
- [ ] Mobile usability score > 80

### Phase 2 Success
- [ ] 80%+ clip uploads succeed on first try
- [ ] Video player works on all major browsers
- [ ] Annotated frames load < 3s
- [ ] Users can share analysis links

### Phase 3 Success
- [ ] Checkout conversion rate > 15%
- [ ] Progress dashboard used by 60%+ paid users
- [ ] Refund request flow works smoothly
- [ ] Stripe webhooks process correctly

---

## Next Steps for Execution

1. **Set up Next.js project** with shadcn/ui
2. **Configure authentication** with NextAuth.js
3. **Build landing page** with clear CTA
4. **Implement magic link flow**
5. **Create Riot ID linking form**
6. **Build analysis request form** (Phase 1)
7. **Design report display** with mock data
8. **Connect to backend API** when ready
9. **Add clip upload UI** (Phase 2)
10. **Integrate video player** with annotations
11. **Build pricing page** (Phase 3)
12. **Integrate Stripe checkout**
13. **Create progress dashboard**
14. **Test all flows end-to-end**
15. **Deploy to Vercel**

---

## Notes for Executing Agent

- Start with Phase 1 features only
- Use mock data until backend is ready
- Prioritize mobile responsiveness from day one
- Keep components simple and reusable
- Document any deviations from this plan
- Test with real Valorant players early
- Iterate based on user feedback
