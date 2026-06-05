'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight, Target, TrendingUp, Zap, Crosshair } from 'lucide-react'
import { Stagger, Item, Reveal, easeOut } from '@/components/ui/motion'
import { AnimatedCounter } from '@/components/ui/AnimatedCounter'

const FEATURES = [
  {
    icon: Target,
    title: 'Aim analysis',
    body: 'Overshoot, undershoot, body-not-head, wrong target, movement errors. Each classified, each scored by impact on your performance.',
  },
  {
    icon: TrendingUp,
    title: 'Riot stats',
    body: 'Your last 20 ranked matches via the official Riot API. Headshot %, ADR, win rate, rank trajectory, top agent and weapon.',
  },
  {
    icon: Zap,
    title: 'AI coaching',
    body: 'Your data fed directly into Claude. Specific numbers, specific problems, specific fixes, not generic tips you have read a hundred times.',
  },
]

const STATS = [
  { value: 20, suffix: '', label: 'matches per report' },
  { value: 6, suffix: '', label: 'mistake types detected' },
  { value: 30, prefix: '<', suffix: 's', label: 'report generation' },
]

export default function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#07080C]">
      {/* Background layers */}
      <div className="pointer-events-none absolute inset-0 bg-radial-glow" />
      <div className="pointer-events-none absolute inset-0 bg-grid aurora" />

      {/* Nav */}
      <nav className="fixed inset-x-0 top-0 z-50 border-b border-[#1F2130] bg-[#07080C]/80 backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center clip-corner-sm bg-gradient-to-br from-[#FF4655] to-[#B8323D]">
              <Crosshair className="h-4 w-4 text-white" />
            </span>
            <span className="font-display text-lg font-bold uppercase tracking-widest">
              <span className="text-[#FF4655]">AimLab</span>
              <span className="text-[#F0F1F5]">VAL</span>
            </span>
          </Link>
          <div className="flex items-center gap-5">
            <Link href="/dashboard" className="hidden text-sm text-[#7A8496] transition hover:text-[#F0F1F5] sm:block">
              Dashboard
            </Link>
            <Link href="/auth/signin" className="text-sm text-[#7A8496] transition hover:text-[#F0F1F5]">
              Sign in
            </Link>
            <Link
              href="/analysis/new"
              className="clip-corner-sm bg-[#FF4655] px-4 py-1.5 text-sm font-semibold text-white transition hover:bg-[#CC3542]"
            >
              Get started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative mx-auto max-w-6xl px-6 pt-40 pb-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: easeOut }}
          className="max-w-3xl"
        >
          <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-[#1F2130] bg-[#111318]/60 px-4 py-1.5 text-xs uppercase tracking-widest text-[#7A8496]">
            <span className="h-1.5 w-1.5 rounded-full bg-[#FF4655] pulse-red" />
            AI coaching · Riot API data · Free to start
          </div>

          <h1 className="font-display text-5xl font-bold leading-[1.05] tracking-tight md:text-7xl">
            Understand why you
            <br />
            <span className="gradient-text text-glow">lose gunfights.</span>
          </h1>

          <p className="mt-6 max-w-xl text-lg leading-relaxed text-[#7A8496]">
            Paste your Riot ID. We pull your last 20 matches, analyse your aim patterns, and give
            you a direct coaching report with specific numbers and specific fixes.
          </p>

          <div className="mt-10 flex flex-wrap items-center gap-4">
            <Link
              href="/analysis/new"
              className="clip-corner group inline-flex items-center gap-2 bg-[#FF4655] px-7 py-3.5 text-sm font-semibold text-white shadow-red-glow transition hover:bg-[#CC3542]"
            >
              Analyze my aim
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              href="/tracker"
              className="inline-flex items-center gap-2 border border-[#1F2130] px-7 py-3.5 text-sm font-semibold text-[#F0F1F5] transition hover:border-[#FF4655]/40"
            >
              View demo tracker
            </Link>
          </div>
        </motion.div>

        {/* Stats */}
        <Stagger className="mt-20 grid grid-cols-1 gap-px overflow-hidden rounded-xl border border-[#1F2130] bg-[#1F2130] sm:grid-cols-3" delay={0.2}>
          {STATS.map((s) => (
            <Item key={s.label} className="bg-[#0B0C12] px-8 py-7">
              <div className="font-display text-4xl font-bold text-[#FF4655]">
                <AnimatedCounter value={s.value} prefix={s.prefix ?? ''} suffix={s.suffix} />
              </div>
              <div className="mt-1 text-xs uppercase tracking-widest text-[#42495A]">{s.label}</div>
            </Item>
          ))}
        </Stagger>
      </section>

      {/* Features */}
      <section className="relative mx-auto max-w-6xl px-6 pb-28">
        <Reveal>
          <p className="mb-2 text-xs uppercase tracking-[0.3em] text-[#FF4655]">What you get</p>
          <h2 className="font-display text-3xl font-bold tracking-tight">Three layers of feedback</h2>
        </Reveal>
        <Stagger className="mt-10 grid gap-5 md:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, body }) => (
            <Item key={title}>
              <motion.div
                whileHover={{ y: -6 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                className="glass glass-hover h-full rounded-xl p-7"
              >
                <span className="mb-5 inline-flex h-11 w-11 items-center justify-center rounded-lg bg-[#FF4655]/10 text-[#FF4655]">
                  <Icon className="h-5 w-5" />
                </span>
                <h3 className="font-display text-lg font-bold tracking-wide">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-[#7A8496]">{body}</p>
              </motion.div>
            </Item>
          ))}
        </Stagger>

        {/* CTA band */}
        <Reveal className="mt-20">
          <div className="relative overflow-hidden rounded-2xl border border-[#FF4655]/20 bg-gradient-to-br from-[#15101a] to-[#0B0C12] px-8 py-12 text-center">
            <div className="pointer-events-none absolute inset-0 bg-grid opacity-40" />
            <div className="relative">
              <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
                Ready to climb?
              </h2>
              <p className="mx-auto mt-3 max-w-md text-[#7A8496]">
                One Riot ID is all it takes. Your first coaching report is free.
              </p>
              <Link
                href="/analysis/new"
                className="clip-corner mt-8 inline-flex items-center gap-2 bg-[#FF4655] px-7 py-3.5 text-sm font-semibold text-white shadow-red-glow transition hover:bg-[#CC3542]"
              >
                Start free analysis
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </Reveal>
      </section>

      {/* Footer */}
      <footer className="relative border-t border-[#1F2130]">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-6 py-6 text-xs text-[#42495A] sm:flex-row">
          <span className="font-display uppercase tracking-widest">AimLab VAL</span>
          <span>Not affiliated with Riot Games. Valorant is a trademark of Riot Games.</span>
        </div>
      </footer>
    </div>
  )
}
