import { Target, TrendingUp, Zap } from 'lucide-react'

const FEATURES = [
  {
    icon: Target,
    title: 'Aim analysis',
    body: 'Overshoot, undershoot, body-not-head, wrong target, movement errors. Each classified, each scored by impact on your performance.',
  },
  {
    icon: TrendingUp,
    title: 'Riot stats',
    body: 'Your last 20 ranked matches via the official Riot data. Headshot %, ADR, win rate, rank trajectory, top agent and weapon.',
  },
  {
    icon: Zap,
    title: 'AI coaching',
    body: 'Your data fed into an AI coach. Specific numbers, specific problems, specific fixes, not generic tips you have read a hundred times.',
  },
]

export function Features() {
  return (
    <section className="relative mx-auto max-w-6xl px-6 py-20">
      <p className="mb-2 text-xs uppercase tracking-[0.3em] text-val-accent">What you get</p>
      <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">Three layers of feedback</h2>

      <div className="mt-12 grid gap-5 md:grid-cols-3">
        {FEATURES.map(({ icon: Icon, title, body }) => (
          <div key={title} className="glass glass-hover h-full rounded-xl p-7">
            <span className="mb-5 inline-flex h-11 w-11 items-center justify-center rounded-lg bg-val-accent/10 text-val-accent">
              <Icon className="h-5 w-5" />
            </span>
            <h3 className="font-display text-lg font-bold tracking-wide">{title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-[#7A8496]">{body}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
