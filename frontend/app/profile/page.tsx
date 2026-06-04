'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { TrendingUp, TrendingDown, Minus, ArrowRight } from 'lucide-react'
import { getAllAnalyses, StoredAnalysis, clearAnalyses } from '@/lib/storage'
import { MOCK_REPORT } from '@/lib/mock/analysis'

const FREE_LIMIT = 10

function Delta({ current, prev, format }: { current: number; prev: number | null; format: (v: number) => string }) {
  if (prev === null) return <span className="text-val-muted text-xs">First analysis</span>
  const d  = current - prev
  const up = d > 0
  const dn = d < 0
  return (
    <span className={`inline-flex items-center gap-1 text-xs ${up ? 'text-val-green' : dn ? 'text-val-red' : 'text-val-muted'}`}>
      {up ? <TrendingUp className="w-3 h-3" /> : dn ? <TrendingDown className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
      {up ? '+' : ''}{format(d)} since first
    </span>
  )
}

export default function ProfilePage() {
  const [analyses, setAnalyses] = useState<StoredAnalysis[]>([])

  useEffect(() => {
    const stored = getAllAnalyses()
    if (stored.length === 0) {
      // show mock
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

  return (
    <div className="p-8 max-w-2xl space-y-6 fade-in">

      <div>
        <p className="text-xs uppercase tracking-widest text-val-muted mb-2">Profile</p>
        <h1 className="font-display text-3xl font-bold tracking-tight">Your Account</h1>
      </div>

      {/* Identity */}
      <div className="border border-val-border bg-val-surface p-6 space-y-3">
        <p className="text-xs uppercase tracking-widest text-val-muted">Identity</p>
        <div className="flex items-baseline gap-3">
          <span className="font-display text-2xl font-bold">
            {riot?.game_name ?? '—'}<span className="text-val-muted">#{riot?.tag_line}</span>
          </span>
          {riot?.current_rank && <span className="text-val-red text-sm">{riot.current_rank}</span>}
        </div>
        <p className="text-val-muted text-xs">
          {analyses.length} analysis{analyses.length !== 1 ? 'es' : ''} saved
          {latest && ` · last run ${new Date(latest.saved_at).toLocaleDateString()}`}
        </p>
        <Link href="/tracker" className="inline-flex items-center gap-1 text-val-red text-xs hover:underline">
          View tracker <ArrowRight className="w-3 h-3" />
        </Link>
      </div>

      {/* Progress */}
      <div className="border border-val-border bg-val-surface p-6 space-y-4">
        <p className="text-xs uppercase tracking-widest text-val-muted">Progress since first analysis</p>
        <div className="grid grid-cols-3 gap-px bg-val-border">
          {[
            {
              label: 'HS%',
              current: riot?.avg_headshot_pct ?? 0,
              prev:    first?.riot_report?.avg_headshot_pct ?? null,
              format:  (v: number) => `${v.toFixed(1)}%`,
            },
            {
              label: 'ADR',
              current: riot?.avg_adr ?? 0,
              prev:    first?.riot_report?.avg_adr ?? null,
              format:  (v: number) => v.toFixed(0),
            },
            {
              label: 'Win rate',
              current: (riot?.win_rate ?? 0) * 100,
              prev:    first?.riot_report ? (first.riot_report.win_rate ?? 0) * 100 : null,
              format:  (v: number) => `${v.toFixed(0)}%`,
            },
          ].map(({ label, current, prev, format }) => (
            <div key={label} className="bg-val-surface p-4">
              <p className="text-val-muted text-xs uppercase tracking-widest mb-2">{label}</p>
              <p className="font-display text-2xl font-bold text-val-text mb-1">{format(current)}</p>
              <Delta current={current} prev={prev} format={format} />
            </div>
          ))}
        </div>
      </div>

      {/* Usage */}
      <div className="border border-val-border bg-val-surface p-6 space-y-3">
        <div className="flex items-center justify-between">
          <p className="text-xs uppercase tracking-widest text-val-muted">Usage</p>
          <span className="text-xs border border-val-border text-val-subtle px-2 py-0.5">Free tier</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-val-subtle">{usedThisMonth} of {FREE_LIMIT} analyses this month</span>
          <span className="text-val-muted text-xs">{FREE_LIMIT - usedThisMonth} remaining</span>
        </div>
        <div className="w-full bg-val-border h-1">
          <div className="h-1 bg-val-red transition-all" style={{ width: `${Math.min(100, (usedThisMonth / FREE_LIMIT) * 100)}%` }} />
        </div>
        <Link href="/settings"
          className="clip-corner-sm inline-flex items-center gap-2 bg-val-red text-white text-xs font-semibold px-3 py-1.5 hover:bg-val-red-dark transition mt-1">
          Upgrade for unlimited →
        </Link>
      </div>

    </div>
  )
}
