import type { Metadata } from 'next'
import { SiteHeader } from '@/components/layout/SiteHeader'
import { SiteFooter } from '@/components/layout/SiteFooter'

export const metadata: Metadata = {
  title: 'Roadmap — AimLab VAL',
  description:
    'What is shipped, in progress, and planned for AimLab VAL: Riot stats and AI coaching, clip analysis, and payments.',
}

type Status = 'Shipped' | 'In progress' | 'Planned'

const STATUS_STYLES: Record<Status, string> = {
  Shipped:       'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
  'In progress': 'border-val-accent/30 bg-val-accent/10 text-val-accent',
  Planned:       'border-[#2A2D40] bg-[#1F2130]/40 text-[#7A8496]',
}

const PHASES: { phase: string; title: string; status: Status; items: string[] }[] = [
  {
    phase: 'Phase 0',
    title: 'Aim detection model',
    status: 'Shipped',
    items: [
      'Custom YOLO model trained on 10k labelled Valorant frames',
      'Detects engagements and crosshair-relative aim errors',
    ],
  },
  {
    phase: 'Phase 1',
    title: 'Stats + AI coaching (live)',
    status: 'Shipped',
    items: [
      'Riot ID lookup and last-20-match pull',
      'Headshot %, ADR, win rate, rank delta, top agent and weapon',
      'AI coaching report with numbers-specific feedback',
      'Tracker, dashboard, and profile with saved history',
    ],
  },
  {
    phase: 'Phase 1B',
    title: 'Accounts + persistence',
    status: 'In progress',
    items: [
      'Magic-link email sign in',
      'Database-backed report storage',
      'Free-tier usage limits and credit tracking',
    ],
  },
  {
    phase: 'Phase 2',
    title: 'Clip analysis',
    status: 'Planned',
    items: [
      'Drag-and-drop clip upload',
      'Frame-by-frame detection of overshoot, undershoot, body-not-head and spray errors',
      'Clip findings merged into the coaching report',
    ],
  },
  {
    phase: 'Phase 3',
    title: 'Payments + launch',
    status: 'Planned',
    items: [
      'Pro subscription at $9/month with a 7-day trial',
      'Unlimited analyses and priority generation',
      'Public launch',
    ],
  },
]

export default function RoadmapPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#070B18]">
      <div className="pointer-events-none absolute inset-0 bg-radial-glow" />
      <SiteHeader />

      <main className="relative mx-auto max-w-3xl px-6 pt-32 pb-24">
        <p className="mb-2 text-xs uppercase tracking-[0.3em] text-val-accent">Roadmap</p>
        <h1 className="font-display text-4xl font-bold tracking-tight md:text-5xl">Where we are headed</h1>
        <p className="mt-4 max-w-xl text-lg leading-relaxed text-[#7A8496]">
          Built in the open. Here is what is shipped, what we are building now, and what is next.
        </p>

        <div className="mt-14 space-y-4">
          {PHASES.map((p) => (
            <div key={p.phase} className="glass rounded-xl p-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <span className="text-xs uppercase tracking-widest text-[#42495A]">{p.phase}</span>
                  <h2 className="font-display text-xl font-bold tracking-wide">{p.title}</h2>
                </div>
                <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${STATUS_STYLES[p.status]}`}>
                  {p.status}
                </span>
              </div>
              <ul className="mt-4 space-y-2">
                {p.items.map((item) => (
                  <li key={item} className="flex items-start gap-2.5 text-sm leading-relaxed text-[#C7CDDA]">
                    <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-val-accent" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </main>

      <SiteFooter />
    </div>
  )
}
