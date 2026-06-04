# Valorant Aim Analyzer - Frontend

A modern, production-ready Next.js 14 frontend for analyzing Valorant player aim and performance using AI-powered insights.

## 🎯 Overview

The Valorant Aim Analyzer frontend provides players with detailed insights into their gameplay, tracking aim patterns, identifying weaknesses, and offering personalized coaching recommendations. Built with Next.js 14, React 18, TypeScript, and Tailwind CSS for a seamless, responsive experience.

**Status**: ✅ Phase 1 (Tracker-Only MVP) - Complete and ready for backend integration

## ✨ Features

### Phase 1: Tracker-Only MVP ✅ COMPLETE
- **Authentication**: Magic link email sign-in with Riot ID linking
- **Analysis Tracking**: Request and view detailed aim analysis reports
- **Dashboard**: Track analysis history and quick stats
- **Reporting**: View detailed performance metrics with AI coaching insights
- **Visualizations**: Weapon performance charts and statistics
- **Responsive Design**: Mobile-first, works on all devices
- **Dark Theme**: Valorant-inspired aesthetic optimized for gaming

### Phase 2: Clip Analysis 🔄 PLANNED
- Video upload with drag & drop
- Frame-by-frame analysis viewer
- Annotated video player
- Engagement timeline visualization
- Combined reports

### Phase 3: Monetization 💳 PLANNED
- Stripe subscription integration
- Usage metering
- Progress tracking
- 7-day free trial

## 🛠️ Tech Stack

| Category | Technology | Version |
|----------|-----------|---------|
| **Framework** | Next.js | 14.2.3 |
| **UI Library** | React | 18.3.1 |
| **Language** | TypeScript | 5.4.2 |
| **Styling** | Tailwind CSS | 3.4.1 |
| **State Management** | Zustand | 4.5.0 |
| **Forms** | React Hook Form + Zod | 7.51.0 + 3.22.4 |
| **Charts** | Recharts | 2.12.0 |
| **Icons** | Lucide React | 0.408.0 |
| **Authentication** | NextAuth.js | 5.0.0-beta |
| **HTTP Client** | Fetch API | Built-in |
| **Deployment** | Vercel | Recommended |

## 📦 Installation

### Prerequisites
- **Node.js**: 18+ (includes npm)
- **Git**: For version control
- **Code Editor**: VS Code recommended

### Quick Start (2 minutes)

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Create environment file**
```bash
cp .env.example .env.local
```

4. **Start development server**
```bash
npm run dev
```

5. **Open in browser**
```
http://localhost:3000
```

## 📁 Project Structure

```
frontend/
├── app/                                  # Next.js 14 App Router
│   ├── layout.tsx                       # Root layout wrapper
│   ├── page.tsx                         # Landing page (/)
│   ├── globals.css                      # Global styles
│   ├── auth/
│   │   ├── signin/page.tsx              # Sign in page (/auth/signin)
│   │   ├── link-riot-id/page.tsx        # Riot ID linking (/auth/link-riot-id)
│   │   └── callback/page.tsx            # OAuth callback (/auth/callback)
│   ├── dashboard/
│   │   ├── layout.tsx                   # Dashboard layout with sidebar
│   │   └── page.tsx                     # Main dashboard (/dashboard)
│   ├── analysis/
│   │   ├── new/page.tsx                 # Create new analysis (/analysis/new)
│   │   └── [id]/page.tsx                # View analysis report (/analysis/[id])
│   ├── settings/page.tsx                # Account settings (/settings)
│   └── api/
│       └── auth/signin/route.ts         # API route handlers
│
├── components/                          # React Components
│   ├── layout/
│   │   ├── Header.tsx                   # Top navigation bar
│   │   └── Sidebar.tsx                  # Dashboard sidebar navigation
│   ├── auth/
│   │   ├── MagicLinkForm.tsx            # Email magic link form
│   │   ├── RiotIdLinkForm.tsx           # Riot ID linking form
│   │   └── AuthGuard.tsx                # Route protection wrapper
│   ├── analysis/
│   │   ├── AnalysisForm.tsx             # Create new analysis form
│   │   ├── ReportView.tsx               # Full analysis report display
│   │   ├── StatsCards.tsx               # Key metrics cards
│   │   └── WeaponStats.tsx              # Weapon charts with Recharts
│   └── dashboard/
│       ├── AnalysisHistory.tsx          # Analysis history table
│       └── QuickStats.tsx               # Quick stats overview
│
├── lib/                                 # Utilities & Helpers
│   ├── api.ts                           # Typed API client
│   ├── store.ts                         # Zustand state stores
│   ├── types.ts                         # TypeScript interfaces
│   ├── constants.ts                     # App-wide constants
│   ├── hooks.ts                         # Custom React hooks
│   └── mock/
│       └── analysis.ts                  # Mock data for development
│
├── public/                              # Static assets
├── package.json                         # Dependencies & scripts
├── tsconfig.json                        # TypeScript configuration
├── next.config.js                       # Next.js configuration
├── tailwind.config.ts                   # Tailwind CSS customization
├── postcss.config.js                    # PostCSS configuration
├── .env.example                         # Environment variables template
├── .gitignore                           # Git ignore rules
├── README.md                            # This file
├── QUICKSTART.md                        # 5-minute setup guide
└── DEPLOYMENT.md                        # Production deployment guide
```

## 📍 Key Pages

### Public Pages
- **`/`** - Landing page with features and CTA
- **`/auth/signin`** - Magic link email authentication
- **`/auth/link-riot-id`** - Riot ID linking form
- **`/auth/callback`** - OAuth callback handler

### Protected Pages
- **`/dashboard`** - Main dashboard with analysis history
- **`/analysis/new`** - Create new analysis request
- **`/analysis/[id]`** - View individual analysis report
- **`/settings`** - Account settings and profile

## 🎨 Design System

### Color Palette (Valorant-Inspired)
```css
Primary (Red):      #FF4655  /* Actions, highlights */
Primary Dark:       #C4323E  /* Hover states */
Secondary (Dark):   #0F1923  /* Background */
Accent (Cyan):      #69C9D0  /* Secondary actions */
Text Primary:       #ECE8E1  /* Main text */
Text Secondary:     #8B9BB4  /* Secondary text */
Surface:            #1F2731  /* Cards, containers */
Surface Hover:      #2A3542  /* Hover states */
```

### Typography
- **Headings**: Inter Bold / Rajdhani Bold (gaming feel)
- **Body**: Inter Regular
- **Monospace**: JetBrains Mono (stats, IDs)

### Responsive Breakpoints
- **Mobile**: < 640px (sm)
- **Tablet**: 640px - 1024px (md)
- **Desktop**: 1024px - 1280px (lg)
- **Large**: 1280px+ (xl, 2xl)

## 🚀 Development

### Available Scripts

```bash
# Start development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run ESLint
npm run lint

# Type check with TypeScript
npm type-check
```

### Development Workflow

1. **Create a feature branch**
```bash
git checkout -b feature/my-feature
```

2. **Make changes** (components update automatically with hot reload)

3. **Test locally**
```bash
npm run dev
# Open http://localhost:3000
```

4. **Commit changes**
```bash
git add .
git commit -m "Add my feature"
```

5. **Push to GitHub**
```bash
git push origin feature/my-feature
```

### Creating Components

**Example: New Component**
```typescript
'use client'  // Mark as client component if needed

import { useState } from 'react'
import { ArrowRight } from 'lucide-react'  // Icons from Lucide

interface MyComponentProps {
  title: string
  onClick: () => void
}

export function MyComponent({ title, onClick }: MyComponentProps) {
  const [isLoading, setIsLoading] = useState(false)

  return (
    <div className="bg-surface-500 border border-secondary-700 rounded-lg p-6">
      <h2 className="text-xl font-bold mb-4">{title}</h2>
      <button
        onClick={onClick}
        disabled={isLoading}
        className="bg-primary-400 text-secondary-900 px-4 py-2 rounded-lg font-semibold hover:bg-primary-500 transition disabled:opacity-50"
      >
        {isLoading ? 'Loading...' : 'Click me'}
        <ArrowRight className="w-4 h-4 ml-2" />
      </button>
    </div>
  )
}
```

### Creating Pages

**Example: New Page**
```typescript
import Link from 'next/link'

export default function MyPage() {
  return (
    <div className="min-h-screen bg-secondary-900 p-8">
      <h1 className="text-3xl font-bold mb-4">My Page</h1>
      <p className="text-secondary-300">Content here</p>
      <Link href="/" className="text-primary-400 hover:text-primary-300">
        Back to home
      </Link>
    </div>
  )
}
```

## 🔌 API Integration

### Current Status
- ✅ Frontend complete with mock data
- ⏳ Backend API needed (see `API_CONTRACT.md`)

### Connecting to Backend

1. **Update environment variables**
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_AUTH_URL=http://localhost:3000
```

2. **API Client Ready**
```typescript
import { analysisApi } from '@/lib/api'

// Create analysis
const result = await analysisApi.createTracker('PlayerName#1234')

// Get analysis
const analysis = await analysisApi.getAnalysis(id)

// Get history
const history = await analysisApi.getHistory()
```

3. **Update Components** - Replace mock data with API calls

### Backend Endpoints Required

See `API_CONTRACT.md` for complete specification:

#### Authentication
- `POST /api/auth/signin` - Send magic link
- `POST /api/auth/callback` - Verify magic link
- `POST /api/auth/link-riot-id` - Link Riot account
- `GET /api/auth/session` - Get current session

#### Analysis
- `POST /api/analysis/tracker` - Request tracker analysis
- `GET /api/analysis/:id` - Get analysis details
- `GET /api/analysis/history` - Get user's analyses

#### User
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update profile

## 🧪 Testing

### Manual Testing
```bash
# Start dev server
npm run dev

# Test flows:
1. Landing page - navigation works
2. Sign in - form validation
3. Riot ID linking - error handling
4. Dashboard - displays mock data
5. Create analysis - form submission
6. View report - charts display
7. Mobile responsive - resize browser
```

### Browser DevTools
- **F12** or Right-click > Inspect
- **Network tab** - See API calls
- **Console tab** - Check for errors
- **React DevTools** - Inspect component tree

### Testing with Backend

When backend is ready:
1. Start backend API on port 3001
2. Update `.env.local` with backend URL
3. Replace mock data imports with API calls
4. Test end-to-end flows

## 📦 State Management

### Zustand Stores

```typescript
import { useAuthStore, useAnalysisStore } from '@/lib/store'

// Auth store
const { user, isAuthenticated, setUser, logout } = useAuthStore()

// Analysis store
const { currentAnalysis, isLoading, setCurrentAnalysis } = useAnalysisStore()
```

### Usage in Components
```typescript
'use client'

import { useAuthStore } from '@/lib/store'

export function MyComponent() {
  const { user, logout } = useAuthStore()

  return (
    <div>
      <p>Welcome, {user?.email}</p>
      <button onClick={logout}>Sign out</button>
    </div>
  )
}
```

## 🎯 Mock Data

### Location
`lib/mock/analysis.ts`

### Contains
- Sample analysis report with stats
- Analysis history (4 records)
- Weapon statistics
- Agent statistics
- Coaching insights

### Using Mock Data
```typescript
import { mockAnalysis, mockAnalysisHistory } from '@/lib/mock/analysis'

// Use in components during development
const analysis = mockAnalysis
const history = mockAnalysisHistory
```

## 🚢 Deployment

### Vercel (Recommended - Zero Config)

1. **Push to GitHub**
```bash
git push origin main
```

2. **Connect to Vercel**
   - Visit https://vercel.com
   - Click "Add New..." > "Project"
   - Select repository
   - Deploy!

3. **Set environment variables**
   - In Vercel dashboard: Settings > Environment Variables
   - Add: `NEXT_PUBLIC_API_URL=<your-api-url>`

### Docker

```dockerfile
# Build
docker build -t valorant-frontend .

# Run
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://api.example.com \
  valorant-frontend
```

### Self-Hosted (VPS)

```bash
# Install Node.js & PM2
npm install -g pm2

# Build & start
npm run build
pm2 start npm --name "frontend" -- start

# Setup reverse proxy with Nginx
# See DEPLOYMENT.md for details
```

### AWS Deployment
- **Amplify**: Connect GitHub repo for auto-deploy
- **EC2**: Manual deployment with PM2 + Nginx
- **CloudFront**: CDN for static assets

See `DEPLOYMENT.md` for detailed deployment instructions.

## 🔒 Security

### Best Practices Implemented
- ✅ No secrets in code (use `.env.local`)
- ✅ Input validation (React Hook Form + Zod)
- ✅ HTTPS/SSL in production
- ✅ CORS configured properly
- ✅ TypeScript for type safety
- ✅ Environment-based configuration

### Environment Setup
Never commit:
- `.env.local` (local secrets)
- API keys or tokens
- Database credentials

Use `.env.example` as template.

## 🧹 Code Quality

### Linting
```bash
npm run lint
```

### Type Checking
```bash
npm type-check
```

### Code Style
- **Format**: ESLint configured
- **Naming**: Camel case for variables/functions
- **Components**: PascalCase for components
- **Files**: kebab-case for file names

## 📊 Performance

### Optimizations Included
- ✅ Next.js Image Optimization
- ✅ Code splitting by route
- ✅ CSS-in-JS with Tailwind
- ✅ Tree-shaking with ES modules
- ✅ Lazy loading with `next/dynamic`

### Monitoring
```bash
# Check bundle size
npm run build

# Lighthouse audit
# In browser: DevTools > Lighthouse
```

## 🐛 Troubleshooting

### Port 3000 Already in Use
```bash
# Use different port
PORT=3001 npm run dev
```

### Module Not Found Error
- Check import paths use `@/` alias
- Verify file exists and is exported
- Clear cache: `rm -rf .next node_modules && npm install`

### Build Fails
```bash
# Clean rebuild
rm -rf .next
npm run build
```

### Environment Variables Not Working
- Restart dev server after `.env.local` changes
- Variables must start with `NEXT_PUBLIC_` for client-side
- Check `.gitignore` includes `.env.local`

### Styles Not Applying
- Verify Tailwind class names are correct
- Check `tailwind.config.ts` is configured
- Restart dev server
- Clear browser cache (Ctrl+Shift+Delete)

## 📚 Documentation

- **README.md** (this file) - Full project overview
- **QUICKSTART.md** - 5-minute developer setup
- **DEPLOYMENT.md** - Production deployment guide
- **API_CONTRACT.md** - API specifications
- **NEXT_STEPS.md** - Integration checklist

## 🤝 Contributing

1. **Fork the repository**
```bash
git clone <your-fork>
cd frontend
```

2. **Create feature branch**
```bash
git checkout -b feature/my-feature
```

3. **Make changes**
   - Write code
   - Test locally
   - Follow code style

4. **Commit with clear message**
```bash
git commit -m "Add: my feature description"
```

5. **Push and create pull request**
```bash
git push origin feature/my-feature
```

## 📞 Support & Resources

### Getting Help
1. Check documentation files
2. Search GitHub Issues
3. Review code comments
4. Check console for errors

### External Resources
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript Docs](https://www.typescriptlang.org)
- [Zustand GitHub](https://github.com/pmndrs/zustand)

### Learning Resources
- Next.js tutorials on official docs
- React patterns and best practices
- Tailwind CSS utility-first approach
- TypeScript for React developers

## 📋 Checklist for New Developers

- [ ] Clone repository
- [ ] Install Node.js 18+
- [ ] Run `npm install` in frontend folder
- [ ] Copy `.env.example` to `.env.local`
- [ ] Run `npm run dev`
- [ ] Open http://localhost:3000
- [ ] Explore pages and components
- [ ] Read QUICKSTART.md
- [ ] Create a test component
- [ ] Make a commit

## 🎓 Next Steps

### For Development
1. Start with `QUICKSTART.md` for fast setup
2. Explore components in `components/`
3. Check `lib/mock/analysis.ts` for data structure
4. Try modifying a component and hot-reload
5. Create your own component

### For Integration
1. Read `API_CONTRACT.md` for backend specs
2. Implement backend endpoints
3. Update `lib/api.ts` with real API calls
4. Replace mock data imports
5. Test end-to-end

### For Deployment
1. Read `DEPLOYMENT.md` for options
2. Choose hosting platform (Vercel recommended)
3. Set up CI/CD if needed
4. Configure environment variables
5. Deploy!

## 📄 License

MIT License - See LICENSE file for details

## 👥 Team

- **Lead Developer**: Eduardo
- **Frontend Framework**: Next.js 14
- **Design**: Valorant-inspired
- **Status**: Phase 1 Complete ✅

## 🚀 Ready to Build?

```bash
cd frontend
npm install
npm run dev
```

Then visit **http://localhost:3000** to see the app! 🎮

---

**Last Updated**: June 4, 2024  
**Status**: Phase 1 Complete - Ready for Backend Integration  
**Next Phase**: Clip Analysis with Video Upload
