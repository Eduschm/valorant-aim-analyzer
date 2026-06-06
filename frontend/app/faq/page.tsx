import type { Metadata } from 'next'
import Link from 'next/link'
import { SiteHeader } from '@/components/layout/SiteHeader'
import { SiteFooter } from '@/components/layout/SiteFooter'
import { FaqAccordion } from '@/components/marketing/FaqAccordion'

export const metadata: Metadata = {
  title: 'FAQ — AimLab VAL',
  description:
    'Frequently asked questions about AimLab VAL: is it allowed by Riot, how accurate is it, is your data safe, what it costs, and which regions are supported.',
}

export default function FaqPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#07080C]">
      <div className="pointer-events-none absolute inset-0 bg-radial-glow" />
      <SiteHeader />

      <main className="relative mx-auto max-w-3xl px-6 pt-32 pb-24">
        <p className="mb-2 text-xs uppercase tracking-[0.3em] text-val-accent">FAQ</p>
        <h1 className="font-display text-4xl font-bold tracking-tight md:text-5xl">
          Frequently asked questions
        </h1>
        <p className="mt-4 max-w-xl text-lg leading-relaxed text-[#7A8496]">
          Everything people ask before their first analysis. Still stuck? Read the{' '}
          <Link href="/guide" className="text-val-accent hover:underline">guide</Link>.
        </p>

        <div className="mt-12">
          <FaqAccordion />
        </div>
      </main>

      <SiteFooter />
    </div>
  )
}
