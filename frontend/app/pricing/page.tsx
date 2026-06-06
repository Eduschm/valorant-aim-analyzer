import type { Metadata } from 'next'
import { SiteHeader } from '@/components/layout/SiteHeader'
import { SiteFooter } from '@/components/layout/SiteFooter'
import { PricingTable } from '@/components/marketing/PricingTable'
import { FaqAccordion } from '@/components/marketing/FaqAccordion'
import { FAQ_ITEMS } from '@/components/marketing/faq-data'

export const metadata: Metadata = {
  title: 'Pricing — AimLab VAL',
  description:
    'Simple pricing for AimLab VAL. Free tier with monthly analyses, or Pro at $9/month for unlimited reports with a 7-day free trial.',
}

// A couple of pricing-specific questions pulled from the shared FAQ set.
const PRICING_FAQ = FAQ_ITEMS.filter((i) => i.q.includes('cost') || i.q.includes('Riot? Will'))

export default function PricingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#07080C]">
      <div className="pointer-events-none absolute inset-0 bg-radial-glow" />
      <SiteHeader />

      <main className="relative mx-auto max-w-4xl px-6 pt-32 pb-24">
        <div className="text-center">
          <p className="mb-2 text-xs uppercase tracking-[0.3em] text-val-accent">Pricing</p>
          <h1 className="font-display text-4xl font-bold tracking-tight md:text-5xl">
            Simple, honest pricing
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-lg leading-relaxed text-[#7A8496]">
            Start free, every month. Upgrade to Pro when you want unlimited analyses. Cancel anytime
            during the 7-day trial.
          </p>
        </div>

        <div className="mt-14">
          <PricingTable />
        </div>

        <section className="mt-20">
          <h2 className="font-display text-2xl font-bold tracking-tight">Pricing questions</h2>
          <div className="mt-6">
            <FaqAccordion items={PRICING_FAQ} />
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  )
}
