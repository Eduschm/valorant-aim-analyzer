import Link from 'next/link'
import { ArrowRight, Target, TrendingUp, Zap, ChevronRight } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-val-bg">

      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-val-border bg-val-bg/90 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <span className="font-display text-xl font-bold tracking-widest text-val-red uppercase">
            AimLab<span className="text-val-text">VAL</span>
          </span>
          <div className="flex items-center gap-4">
            <Link href="/auth/signin" className="text-val-subtle text-sm hover:text-val-text transition">
              Sign in
            </Link>
            <Link href="/auth/signin"
              className="clip-corner-sm bg-val-red text-white text-sm font-semibold px-4 py-1.5 hover:bg-val-red-dark transition">
              Get started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-24 px-6 max-w-6xl mx-auto">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 border border-val-red/30 bg-val-red/5 px-3 py-1 text-val-red text-xs font-semibold uppercase tracking-widest mb-8">
            <span className="w-1.5 h-1.5 bg-val-red rounded-full pulse-red" />
            AI-Powered Aim Coaching
          </div>

          <h1 className="font-display text-6xl md:text-7xl font-bold leading-tight tracking-tight mb-6">
            STOP GUESSING<br />
            <span className="text-val-red">WHY YOU LOSE</span><br />
            GUNFIGHTS.
          </h1>

          <p className="text-val-subtle text-lg mb-10 max-w-xl leading-relaxed">
            Paste your Riot ID. Get a precise breakdown of your aiming mistakes and
            a personalised coaching report in under 30 seconds.
          </p>

          <div className="flex items-center gap-4">
            <Link href="/analysis/new"
              className="clip-corner inline-flex items-center gap-2 bg-val-red text-white font-semibold px-6 py-3 hover:bg-val-red-dark transition shadow-red-glow">
              Analyze my aim
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link href="/auth/signin" className="text-val-subtle text-sm hover:text-val-text transition flex items-center gap-1">
              Sign in <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="max-w-6xl mx-auto px-6">
        <div className="h-px bg-gradient-to-r from-val-red/50 via-val-border to-transparent" />
      </div>

      {/* Stats bar */}
      <section className="max-w-6xl mx-auto px-6 py-12">
        <div className="grid grid-cols-3 gap-0 divide-x divide-val-border">
          {[
            { n: '20', label: 'matches analyzed per report' },
            { n: '6',  label: 'mistake types detected' },
            { n: '<30s', label: 'average report time' },
          ].map(({ n, label }) => (
            <div key={label} className="px-8 py-4 first:pl-0">
              <div className="font-display text-4xl font-bold text-val-red">{n}</div>
              <div className="text-val-subtle text-sm mt-1">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 pb-32">
        <div className="grid md:grid-cols-3 gap-px bg-val-border">
          {[
            {
              icon: Target,
              title: 'Aim Mistake Detection',
              body: 'Overshoot, undershoot, body-not-head, wrong target, movement errors — each classified and scored by impact.',
            },
            {
              icon: TrendingUp,
              title: 'Riot Stats Analysis',
              body: 'Pulls your last 20 matches via the Riot API. Headshot %, ADR, win rate, top agents and weapons.',
            },
            {
              icon: Zap,
              title: 'AI Coaching Report',
              body: 'Claude AI synthesises your stats into a direct, specific coaching report with actionable tips referencing your actual numbers.',
            },
          ].map(({ icon: Icon, title, body }) => (
            <div key={title} className="bg-val-surface p-8 hover:bg-val-surface-2 transition group">
              <div className="w-10 h-10 border border-val-red/40 bg-val-red/5 flex items-center justify-center mb-5 group-hover:border-val-red transition">
                <Icon className="w-5 h-5 text-val-red" />
              </div>
              <h3 className="font-display text-lg font-bold mb-2 tracking-wide">{title}</h3>
              <p className="text-val-subtle text-sm leading-relaxed">{body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-val-border py-8 px-6 text-center text-val-muted text-sm">
        AimLab VAL — Not affiliated with Riot Games.
      </footer>
    </div>
  )
}
