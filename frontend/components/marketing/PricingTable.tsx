import Link from 'next/link'
import { Check } from 'lucide-react'
import { FREE_TIER } from '@/lib/constants'

const PLANS = [
  {
    name: 'Free',
    price: '$0',
    cadence: 'forever',
    highlight: false,
    cta: 'Start free',
    features: [
      `${FREE_TIER.CLIPS_PER_MONTH} analyses per month`,
      'Last 20 ranked matches',
      'AI coaching report',
      'Aim + Riot stat breakdown',
      'Saved tracker history',
    ],
  },
  {
    name: 'Pro',
    price: '$9',
    cadence: 'per month',
    highlight: true,
    cta: 'Upgrade to Pro',
    features: [
      'Unlimited analyses',
      'Priority report generation',
      'Full match history depth',
      'Week-over-week trend charts',
      'Clip analysis (Phase 2) included',
      '7-day free trial',
    ],
  },
]

export function PricingTable({ compact = false }: { compact?: boolean }) {
  return (
    <div className={`grid gap-5 ${compact ? 'sm:grid-cols-2' : 'mx-auto max-w-3xl sm:grid-cols-2'}`}>
      {PLANS.map((plan) => (
        <div
          key={plan.name}
          className={`relative flex flex-col rounded-2xl p-7 ${
            plan.highlight
              ? 'border border-val-accent/40 bg-gradient-to-br from-val-accent/[0.08] to-transparent shadow-accent-glow-sm'
              : 'glass'
          }`}
        >
          {plan.highlight && (
            <span className="absolute right-6 top-6 rounded-full bg-val-accent/15 px-2.5 py-0.5 text-xs font-semibold text-val-accent">
              Most popular
            </span>
          )}
          <h3 className="font-display text-xl font-bold tracking-wide">{plan.name}</h3>
          <div className="mt-3 flex items-baseline gap-1.5">
            <span className="font-display text-4xl font-bold text-[#F0F1F5]">{plan.price}</span>
            <span className="text-sm text-[#7A8496]">/ {plan.cadence}</span>
          </div>

          <ul className="mt-6 flex-1 space-y-3">
            {plan.features.map((f) => (
              <li key={f} className="flex items-start gap-2.5 text-sm text-[#C7CDDA]">
                <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-val-accent" />
                {f}
              </li>
            ))}
          </ul>

          <Link
            href="/auth/signin"
            className={`clip-corner-sm mt-7 inline-flex items-center justify-center px-5 py-2.5 text-sm font-semibold transition ${
              plan.highlight
                ? 'bg-val-accent text-white hover:bg-val-accent-dark'
                : 'border border-[#1F2130] text-[#F0F1F5] hover:border-val-accent/40'
            }`}
          >
            {plan.cta}
          </Link>
        </div>
      ))}
    </div>
  )
}
