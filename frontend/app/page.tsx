import type { Metadata } from 'next'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { SiteHeader } from '@/components/layout/SiteHeader'
import { SiteFooter } from '@/components/layout/SiteFooter'
import { Hero } from '@/components/marketing/Hero'
import { HowItWorks } from '@/components/marketing/HowItWorks'
import { Features } from '@/components/marketing/Features'
import { ImprovementChart } from '@/components/marketing/ImprovementChart'
import { Testimonials } from '@/components/marketing/Testimonials'
import { PricingTable } from '@/components/marketing/PricingTable'

export const metadata: Metadata = {
  title: 'AimLab VAL — AI aim analysis for Valorant',
  description:
    'Paste your Riot ID and get a numbers-specific Valorant coaching report. Headshot %, ADR, win rate, rank trends, and AI feedback on why you lose gunfights.',
}

export default function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#070B18]">
      {/* Background layers */}
      <div className="pointer-events-none absolute inset-0 bg-radial-glow" />
      <div className="pointer-events-none absolute inset-0 bg-grid aurora" />

      <SiteHeader />

      <main className="relative">
        <Hero />
        <HowItWorks />
        <Features />
        <ImprovementChart />
        <Testimonials />

        {/* Pricing teaser */}
        <section className="relative mx-auto max-w-6xl px-6 py-20">
          <p className="mb-2 text-xs uppercase tracking-[0.3em] text-val-accent">Pricing</p>
          <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
            Start free. Upgrade when you are climbing.
          </h2>
          <p className="mt-3 max-w-xl text-sm leading-relaxed text-[#7A8496]">
            Your first reports every month are free. Go Pro for unlimited analyses and a 7-day trial.
          </p>
          <div className="mt-10">
            <PricingTable compact />
          </div>
          <div className="mt-6">
            <Link href="/pricing" className="text-sm text-val-accent hover:underline">
              See full pricing →
            </Link>
          </div>
        </section>

        {/* CTA band */}
        <section className="relative mx-auto max-w-6xl px-6 pb-24">
          <div className="relative overflow-hidden rounded-2xl border border-val-accent/20 bg-gradient-to-br from-[#0e1330] to-[#0C1028] px-8 py-12 text-center">
            <div className="pointer-events-none absolute inset-0 bg-grid opacity-40" />
            <div className="relative">
              <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">Ready to climb?</h2>
              <p className="mx-auto mt-3 max-w-md text-[#7A8496]">
                One Riot ID is all it takes. Your first coaching report is free.
              </p>
              <Link
                href="/#analyze"
                className="clip-corner mt-8 inline-flex items-center gap-2 bg-val-accent px-7 py-3.5 text-sm font-semibold text-white shadow-accent-glow transition hover:bg-val-accent-dark"
              >
                Start free analysis
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  )
}
