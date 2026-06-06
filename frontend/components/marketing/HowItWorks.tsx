import { ClipboardPaste, Database, Sparkles } from 'lucide-react'

const STEPS = [
  {
    icon: ClipboardPaste,
    step: '01',
    title: 'Paste your Riot ID',
    body: 'Drop in your Name#TAG and region. No download, no account needed to start.',
  },
  {
    icon: Database,
    step: '02',
    title: 'We pull your last 20 matches',
    body: 'Headshot %, ADR, win rate, rank trajectory, top agent and weapon — straight from your competitive history.',
  },
  {
    icon: Sparkles,
    step: '03',
    title: 'Get a numbers-specific report',
    body: 'Your stats go to an AI coach that names your single biggest weakness and gives fixes tied to real numbers.',
  },
]

export function HowItWorks() {
  return (
    <section className="relative mx-auto max-w-6xl px-6 py-20">
      <p className="mb-2 text-xs uppercase tracking-[0.3em] text-val-accent">How it works</p>
      <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
        From Riot ID to coaching in under a minute
      </h2>

      <div className="mt-12 grid gap-5 md:grid-cols-3">
        {STEPS.map(({ icon: Icon, step, title, body }) => (
          <div key={step} className="glass rounded-xl p-7">
            <div className="mb-5 flex items-center justify-between">
              <span className="inline-flex h-11 w-11 items-center justify-center rounded-lg bg-val-accent/10 text-val-accent">
                <Icon className="h-5 w-5" />
              </span>
              <span className="font-display text-2xl font-bold text-[#1F2130]">{step}</span>
            </div>
            <h3 className="font-display text-lg font-bold tracking-wide">{title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-[#7A8496]">{body}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
