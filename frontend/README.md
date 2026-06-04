# Valorant Aim Analyzer - Frontend

A modern Next.js 14 frontend for analyzing Valorant player aim and performance.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI Library**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand
- **Forms**: React Hook Form + Zod
- **Data Fetching**: SWR / TanStack Query (ready to integrate)
- **Charts**: Recharts
- **Icons**: Lucide React
- **Authentication**: NextAuth.js (ready to integrate)
- **Deployment**: Vercel

## Project Structure

```
frontend/
├── app/                         # Next.js 14 App Router
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Landing page
│   ├── globals.css             # Global styles
│   ├── auth/
│   │   ├── signin/page.tsx     # Sign in page
│   │   ├── link-riot-id/page.tsx
│   │   └── callback/page.tsx
│   ├── dashboard/
│   │   ├── layout.tsx          # Dashboard layout with sidebar
│   │   └── page.tsx            # Main dashboard
│   ├── analysis/
│   │   ├── new/page.tsx        # Create new analysis
│   │   └── [id]/page.tsx       # View analysis report
│   ├── settings/page.tsx       # Account settings
│   └── api/                    # API routes (proxy to backend)
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   └── Sidebar.tsx
│   ├── auth/
│   │   ├── MagicLinkForm.tsx
│   │   ├── RiotIdLinkForm.tsx
│   │   └── AuthGuard.tsx
│   ├── analysis/
│   │   ├── AnalysisForm.tsx
│   │   ├── ReportView.tsx
│   │   ├── StatsCards.tsx
│   │   └── WeaponStats.tsx
│   └── dashboard/
│       ├── AnalysisHistory.tsx
│       └── QuickStats.tsx
├── lib/
│   ├── api.ts                  # API client
│   ├── store.ts                # Zustand stores
│   └── mock/
│       └── analysis.ts         # Mock data for development
├── public/                     # Static assets
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
└── postcss.config.js
```

## Getting Started

### Installation

```bash
# Install dependencies
npm install

# Or with yarn
yarn install

# Or with pnpm
pnpm install
```

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_AUTH_URL=http://localhost:3000
```

### Development Server

```bash
npm run dev
# Server runs at http://localhost:3000
```

### Build for Production

```bash
npm run build
npm start
```

## Features (Phase 1 - MVP)

### Authentication
- ✅ Magic link email authentication
- ✅ Riot ID linking form
- ✅ Session management

### Analysis Tracking
- ✅ Request new tracker-only analysis
- ✅ View analysis report with stats cards
- ✅ Weapon performance breakdown
- ✅ Coaching insights display

### Dashboard
- ✅ Analysis history table
- ✅ Quick stats cards
- ✅ Recent performance summary

### UI/UX
- ✅ Valorant-inspired dark theme
- ✅ Responsive mobile-friendly design
- ✅ Loading states and error handling
- ✅ Smooth transitions and animations

## API Integration

The frontend is set up to communicate with the backend API. Update the endpoint calls in:

1. **`lib/api.ts`** - API client with endpoints
2. **`app/api/*`** - Next.js API routes (proxy layer)

Example usage in components:

```typescript
import { analysisApi } from '@/lib/api'

// Create new analysis
const result = await analysisApi.createTracker('Edu#1234')

// Fetch analysis details
const analysis = await analysisApi.getAnalysis('analysis_123')

// Get analysis history
const history = await analysisApi.getHistory()
```

## State Management

Using Zustand for global state:

```typescript
import { useAuthStore, useAnalysisStore } from '@/lib/store'

// In components
const { user, isAuthenticated, setUser, logout } = useAuthStore()
const { currentAnalysis, setCurrentAnalysis } = useAnalysisStore()
```

## Mock Data

While developing, the app uses mock data from `lib/mock/analysis.ts`. This includes:
- Sample analysis reports
- Analysis history
- Weapon statistics
- Coaching insights

Replace with real API calls by updating component imports.

## Forms & Validation

Components use React Hook Form with Zod validation:

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'

// Form implementation with validation
```

## Styling

- **Tailwind CSS** for utility-first styling
- **Custom theme** with Valorant-inspired colors
- **Dark mode** by default
- **Responsive breakpoints**: sm, md, lg, xl, 2xl

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import repository to Vercel
3. Configure environment variables in Vercel dashboard
4. Deploy automatically on every push

```bash
# Or deploy manually
npm install -g vercel
vercel
```

### Docker

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY . .
RUN npm ci && npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --only=production
EXPOSE 3000
CMD ["npm", "start"]
```

## Development Checklist

- [ ] Connect to backend API (replace mock data)
- [ ] Implement NextAuth.js authentication
- [ ] Add error boundaries
- [ ] Implement loading skeletons
- [ ] Add toast notifications
- [ ] Set up analytics
- [ ] Add social sharing
- [ ] Implement dark/light theme toggle
- [ ] Add PWA capabilities
- [ ] Performance optimization

## Next Phases

### Phase 2: Clip Analysis
- Video upload with drag & drop
- Annotated video player
- Engagement timeline visualization
- Frame-by-frame analysis viewer

### Phase 3: Monetization
- Stripe integration
- Pricing page
- Usage metering
- Progress tracking dashboard
- 7-day trial flow

## Contributing

1. Create a feature branch
2. Make changes with proper TypeScript types
3. Test thoroughly
4. Submit pull request

## License

MIT
