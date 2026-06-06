import type { Metadata } from 'next'
import Link from 'next/link'
import { Target, Swords, Trophy, TrendingUp, ArrowRight } from 'lucide-react'
import { SiteHeader } from '@/components/layout/SiteHeader'
import { SiteFooter } from '@/components/layout/SiteFooter'

export const metadata: Metadata = {
  title: 'Guide — How AimLab VAL works',
  description:
    'Step-by-step guide to AimLab VAL: enter your Riot ID, understand what each stat means (headshot %, ADR, win rate, rank delta), and read your AI coaching report.',
}

const STATS = [
  {
    icon: Target,
    name: 'Headshot %',
    body: 'Share of your hits that land on the head. The single strongest signal of raw aim. Pros sit around 25-35% in ranked. If yours is low, your crosshair is below head level or you are panic-spraying.',
  },
  {
    icon: Swords,
    name: 'ADR (Average Damage per Round)',
    body: 'How much damage you deal each round. Rewards consistent trades, not just kills. A high ADR with a low K/D usually means you are softening enemies for your team. Below ~120 means you are getting traded before you contribute.',
  },
  {
    icon: Trophy,
    name: 'Win rate',
    body: 'Percentage of your last 20 ranked games won. Above 50% over a sample this size means you are climbing. We pair it with your stats so you can see whether your aim or your impact is driving results.',
  },
  {
    icon: TrendingUp,
    name: 'Rank delta',
    body: 'How many competitive tiers you moved across the games we pulled. Positive means you climbed, negative means you slipped. Read it alongside HS% and ADR trends to see what changed.',
  },
]

export default function GuidePage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#07080C]">
      <div className="pointer-events-none absolute inset-0 bg-radial-glow" />
      <SiteHeader />

      <main className="relative mx-auto max-w-3xl px-6 pt-32 pb-24">
        <p className="mb-2 text-xs uppercase tracking-[0.3em] text-val-accent">Guide</p>
        <h1 className="font-display text-4xl font-bold tracking-tight md:text-5xl">How it works</h1>
        <p className="mt-4 max-w-xl text-lg leading-relaxed text-[#7A8496]">
          Everything you need to go from a Riot ID to a coaching report you can act on.
        </p>

        {/* Getting started */}
        <section className="mt-14">
          <h2 className="font-display text-2xl font-bold tracking-tight">Getting started</h2>
          <ol className="mt-6 space-y-4">
            {[
              'Go to the home page and type your Riot ID in the form, in the format Name#TAG (for example TenZ#NA1).',
              'Pick your region. The autocomplete will suggest matching accounts as you type.',
              'Hit Analyze. We pull your last 20 ranked matches and generate the report in under a minute.',
            ].map((step, i) => (
              <li key={i} className="flex gap-4">
                <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-val-accent/10 font-display text-sm font-bold text-val-accent">
                  {i + 1}
                </span>
                <p className="pt-0.5 text-sm leading-relaxed text-[#C7CDDA]">{step}</p>
              </li>
            ))}
          </ol>
        </section>

        {/* What the stats mean */}
        <section className="mt-16">
          <h2 className="font-display text-2xl font-bold tracking-tight">What each stat means</h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {STATS.map(({ icon: Icon, name, body }) => (
              <div key={name} className="glass rounded-xl p-6">
                <span className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-val-accent/10 text-val-accent">
                  <Icon className="h-5 w-5" />
                </span>
                <h3 className="font-display text-lg font-bold tracking-wide">{name}</h3>
                <p className="mt-2 text-sm leading-relaxed text-[#7A8496]">{body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Reading the report */}
        <section className="mt-16">
          <h2 className="font-display text-2xl font-bold tracking-tight">Reading your report</h2>
          <div className="mt-6 space-y-4 text-sm leading-relaxed text-[#C7CDDA]">
            <p>
              The top of the report shows your rank, the stat cards, and your top agent. Below that, the
              AI coaching section names your <span className="text-val-accent">single biggest weakness</span> and
              gives you a short list of fixes, each tied to a real number from your matches.
            </p>
            <p>
              Run a new analysis after a few sessions and open the{' '}
              <Link href="/tracker" className="text-val-accent hover:underline">Tracker</Link> to watch your
              headshot % and ADR trend over time. Improvement you can see is improvement you will keep.
            </p>
          </div>
        </section>

        <div className="mt-16 flex flex-wrap gap-4">
          <Link
            href="/#analyze"
            className="clip-corner inline-flex items-center gap-2 bg-val-accent px-6 py-3 text-sm font-semibold text-white shadow-accent-glow transition hover:bg-val-accent-dark"
          >
            Analyze my aim <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            href="/faq"
            className="inline-flex items-center gap-2 border border-[#1F2130] px-6 py-3 text-sm font-semibold text-[#F0F1F5] transition hover:border-val-accent/40"
          >
            Read the FAQ
          </Link>
        </div>
      </main>

      <SiteFooter />
    </div>
  )
}
