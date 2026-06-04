# Quick Start Guide

## First Time Setup (5 minutes)

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Create Environment File
```bash
cp .env.example .env.local
```

### 3. Start Development Server
```bash
npm run dev
```

Visit http://localhost:3000 in your browser.

## Common Tasks

### Create a New Page
1. Create file in `app/[name]/page.tsx`
2. Export default function component
3. Use client components with `'use client'` directive for interactivity

Example:
```typescript
export default function MyPage() {
  return <div>Hello World</div>
}
```

### Create a New Component
1. Create file in `components/[category]/MyComponent.tsx`
2. Use `'use client'` if component has state/events
3. Export named function

Example:
```typescript
'use client'

import { useState } from 'react'

export function MyComponent() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(count + 1)}>Count: {count}</button>
}
```

### Add New API Endpoint
1. Create file: `app/api/[route]/route.ts`
2. Export HTTP method function

Example:
```typescript
export async function GET(request: Request) {
  return Response.json({ message: 'Hello' })
}
```

### Use API Client
```typescript
import { analysisApi } from '@/lib/api'

// In a component or server action
const analysis = await analysisApi.getAnalysis('123')
```

### Style with Tailwind
```typescript
<div className="bg-primary-400 text-secondary-900 p-4 rounded-lg hover:bg-primary-500 transition">
  Styled element
</div>
```

### Add Loading State
```typescript
'use client'

import { useState } from 'react'

export function MyButton() {
  const [loading, setLoading] = useState(false)

  const handleClick = async () => {
    setLoading(true)
    try {
      // Do something
    } finally {
      setLoading(false)
    }
  }

  return <button disabled={loading}>{loading ? 'Loading...' : 'Click me'}</button>
}
```

## File Organization

```
components/
├── layout/        # Navigation, headers, footers
├── auth/          # Auth forms, guards
├── analysis/      # Analysis-related components
├── dashboard/     # Dashboard widgets
└── ui/            # Base/reusable components
```

## Testing Locally

### With Mock Data
- App already uses mock data from `lib/mock/analysis.ts`
- No backend needed - just run `npm run dev`

### With Real Backend
1. Start backend API on port 3001
2. Update `NEXT_PUBLIC_API_URL` in `.env.local`
3. Replace mock data imports with API calls

## Debugging

### Browser DevTools
- F12 or Right-click > Inspect
- Network tab to see API calls
- Console tab for errors
- React DevTools extension (recommended)

### VS Code
- Install "Next.js Full Stack" extension
- Set breakpoints in code
- Press F5 to debug

### Console Logging
```typescript
console.log('Debug:', value)
console.error('Error:', error)
```

## Common Issues & Solutions

### Port 3000 already in use
```bash
# Use different port
PORT=3001 npm run dev
```

### Module not found errors
- Check import paths use `@/` alias
- Verify file exists and exported correctly
- Try clearing `.next` folder: `rm -rf .next`

### Build fails
```bash
# Clear cache and rebuild
rm -rf node_modules .next
npm install
npm run build
```

### Environment variables not working
- Restart dev server after changing `.env.local`
- Variables must start with `NEXT_PUBLIC_` for client-side
- Check `.gitignore` includes `.env.local`

## Performance Tips

1. Use `next/image` for images (auto-optimization)
2. Lazy load with `next/dynamic`
3. Memoize expensive components with `React.memo`
4. Use `useCallback` for event handlers
5. Check bundle size: `npm run build`

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Add my feature"

# Push to GitHub
git push origin feature/my-feature

# Create pull request on GitHub
```

## Useful Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start dev server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Check code quality |
| `npm type-check` | Type check TypeScript |

## Resources

- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript Docs](https://www.typescriptlang.org)
- [Zustand](https://github.com/pmndrs/zustand)

## Getting Help

1. Check if similar issue exists in GitHub Issues
2. Search [Stack Overflow](https://stackoverflow.com/questions/tagged/nextjs)
3. Ask in team Slack/Discord
4. Check component docs: `/* JSDoc comments */`

---

**Ready to code?** Start with `npm run dev` 🚀
