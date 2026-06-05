'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus, ArrowRight } from 'lucide-react'
import { getAllAnalyses, StoredAnalysis } from '@/lib/storage'
import { MOCK_REPORT } from '@/lib/mock/analysis'
import { PageTransition } from '@/components/ui/PageTransition'
import { Reveal } from '@/components/ui/motion'

const FREE_LIMIT = 10

function Delta({ current, prev, format }: { current: number; prev: number | null; format: (v: number) => string }) {
  if (prev === null) return <span className="text-xs text-[#42495A]">First analysis</span>
  const d  = current - prev
  const up = d > 0
  const dn = d < 0
  return (
    <span className={`inline-flex items-center gap-1 text-xs ${up ? 'text-emerald-400' : dn ? 'text-[#FF4655]' : 'text-[#42495A]'}`}>
      {up ? <TrendingUp className="h-3 w-3" /> : dn ? <TrendingDown className="h-3 w-3" /> : <Minus className="h-3 w-3" />}
      {up ? '+' : ''}{format(d)} since first
    </span>
  )
}

export default function ProfilePage() {
  const [analyses, setAnalyses] = useState<StoredAnalysis[]>([])

  useEffect(() => {
    const stored = getAllAnalyses()
    if (stored.length === 0) {
      setAnalyses([{
        id: 'mock-001', riot_id: 'DemoPlayer#NA1', saved_at: new Date().toISOString(),
        riot_report: MOCK_REPORT.riot_report as any,
        coaching:    MOCK_REPORT.coaching   as any,
      }])
    } else {
      setAnalyses(stored)
    }
  }, [])

  const latest = analyses[0]
  const first  = analyses[analyses.length - 1]
  const riot   = latest?.riot_report

  const usedThisMonth = analyses.filter(a => {
    const d = new Date(a.saved_at)
    const n = new Date()
    return d.getMonth() === n.getMonth() && d.getFullYear() === n.getFullYear()
  }).length

  const progress = [
    { label: 'HS%', current: riot?.avg_headshot_pct ?? 0, prev: first?.riot_report?.avg_headshot_pct ?? null, format: (v: number) => `${v.toFixed(1)}%` },
    { label: 'ADR', current: riot?.avg_adr ?? 0, prev: first?.riot_report?.avg_adr ?? null, format: (v: number) => v.toFixed(0) },
    { label: 'Win rate', current: (riot?.win_rate ?? 0) * 100, prev: first?.riot_report ? (first.riot_report.win_rate ?? 0) * 100 : null, format: (v: number) => `${v.toFixed(0)}%` },
  ]

  return (
    <PageTransition className="mx-auto max-w-2xl space-y-6 p-6 sm:p-8">

      <div>
        <p className="mb-2 text-xs uppercase tracking-[0.3em] text-[#FF4655]">Profile</p>
        <h1 className="font-display text-3xl font-bold tracking-tight">Your Account</h1>
      </div>

      {/* Identity */}
      <Reveal>
        <div className="glass space-y-3 rounded-xl p-6">
          <p className="text-xs uppercase tracking-widest text-[#42495A]">Identity</p>
          <div className="flex items-baseline gap-3">
            <span className="font-display text-2xl font-bold">
              {riot?.game_name ?? '-'}<span className="text-[#42495A]">#{riot?.tag_line}</span>
            </span>
            {riot?.current_rank && (
              <span className="rounded-full border border-[#FF4655]/30 bg-[#FF4655]/10 px-2.5 py-0.5 text-sm font-semibold text-[#FF4655]">
                {riot.current_rank}
              </span>
            )}
          </div>
          <p className="text-xs text-[#42495A]">
            {analyses.length} analysis{analyses.length !== 1 ? 'es' : ''} saved
            {latest && ` · last run ${new Date(latest.saved_at).toLocaleDateString()}`}
          </p>
          <Link href="/tracker" className="inline-flex items-center gap-1 text-xs text-[#FF4655] hover:underline">
            View tracker <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
      </Reveal>

      {/* Progress */}
      <Reveal delay={0.05}>
        <div className="glass space-y-4 rounded-xl p-6">
          <p className="text-xs uppercase tracking-widest text-[#42495A]">Progress since first analysis</p>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {progress.map(({ label, current, prev, format }) => (
              <div key={label} className="rounded-lg border border-[#1F2130] bg-[#0B0C12] p-4">
                <p className="mb-2 text-xs uppercase tracking-widest text-[#42495A]">{label}</p>
                <p className="mb-1 font-display text-2xl font-bold text-[#F0F1F5]">{format(current)}</p>
                <Delta current={current} prev={prev} format={format} />
              </div>
            ))}
          </div>
        </div>
      </Reveal>

      {/* Usage */}
      <Reveal delay={0.1}>
        <div className="glass space-y-3 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <p className="text-xs uppercase tracking-widest text-[#42495A]">Usage</p>
            <span className="rounded-full border border-[#1F2130] px-2 py-0.5 text-xs text-[#7A8496]">Free tier</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-[#7A8496]">{usedThisMonth} of {FREE_LIMIT} analyses this month</span>
            <span className="text-xs text-[#42495A]">{FREE_LIMIT - usedThisMonth} remaining</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-[#1F2130]">
            <motion.div
              className="h-1.5 rounded-full bg-gradient-to-r from-[#FF4655] to-[#B8323D]"
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(100, (usedThisMonth / FREE_LIMIT) * 100)}%` }}
              transition={{ duration: 0.9, ease: 'easeOut' }}
            />
          </div>
          <Link
            href="/settings"
            className="clip-corner-sm mt-1 inline-flex items-center gap-2 bg-[#FF4655] px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-[#CC3542]"
          >
            Upgrade for unlimited <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
      </Reveal>

    </PageTransition>
  )
}
