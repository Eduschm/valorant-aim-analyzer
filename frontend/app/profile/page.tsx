'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { TrendingUp, TrendingDown, Minus, ArrowRight } from 'lucide-react'
import { getAllAnalyses, StoredAnalysis } from '@/lib/storage'
import { MOCK_REPORT } from '@/lib/mock/analysis'

const FREE_LIMIT = 10

function Delta({ current, prev, format }: { current: number; prev: number | null; format: (v: number) => string }) {
  if (prev === null) return <span className="text-[#42495A] text-xs">First analysis</span>
  const d  = current - prev
  const up = d > 0
  const dn = d < 0
  return (
    <span className={`inline-flex items-center gap-1 text-xs ${up ? 'text-green-400' : dn ? 'text-[#FF4655]' : 'text-[#42495A]'}`}>
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
        <p className="text-xs uppercase tracking-widest text-[#42495A] mb-2">Profile</p>
        <h1 className="font-display text-3xl font-bold tracking-tight">Your Account</h1>
      </div>

      {/* Identity */}
      <div className="border border-[#1F2130] bg-[#111318] p-6 space-y-3">
        <p className="text-xs uppercase tracking-widest text-[#42495A]">Identity</p>
        <div className="flex items-baseline gap-3">
          <span className="font-display text-2xl font-bold">
            {riot?.game_name ?? '—'}<span className="text-[#42495A]">#{riot?.tag_line}</span>
          </span>
          {riot?.current_rank && <span className="text-[#FF4655] text-sm">{riot.current_rank}</span>}
        </div>
        <p className="text-[#42495A] text-xs">
          {analyses.length} analysis{analyses.length !== 1 ? 'es' : ''} saved
          {latest && ` · last run ${new Date(latest.saved_at).toLocaleDateString()}`}
        </p>
        <Link href="/tracker" className="inline-flex items-center gap-1 text-[#FF4655] text-xs hover:underline">
          View tracker <ArrowRight className="w-3 h-3" />
        </Link>
      </div>

      {/* Progress */}
      <div className="border border-[#1F2130] bg-[#111318] p-6 space-y-4">
        <p className="text-xs uppercase tracking-widest text-[#42495A]">Progress since first analysis</p>
        <div className="grid grid-cols-3 gap-px bg-[#1F2130]">
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
            <div key={label} className="bg-[#111318] p-4">
              <p className="text-[#42495A] text-xs uppercase tracking-widest mb-2">{label}</p>
              <p className="font-display text-2xl font-bold text-[#F0F1F5] mb-1">{format(current)}</p>
              <Delta current={current} prev={prev} format={format} />
            </div>
          ))}
        </div>
      </div>

      {/* Usage */}
      <div className="border border-[#1F2130] bg-[#111318] p-6 space-y-3">
        <div className="flex items-center justify-between">
          <p className="text-xs uppercase tracking-widest text-[#42495A]">Usage</p>
          <span className="text-xs border border-[#1F2130] text-[#7A8496] px-2 py-0.5">Free tier</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-[#7A8496]">{usedThisMonth} of {FREE_LIMIT} analyses this month</span>
          <span className="text-[#42495A] text-xs">{FREE_LIMIT - usedThisMonth} remaining</span>
        </div>
        <div className="w-full bg-[#1F2130] h-1">
          <div className="h-1 bg-[#FF4655] transition-all" style={{ width: `${Math.min(100, (usedThisMonth / FREE_LIMIT) * 100)}%` }} />
        </div>
        <Link href="/settings"
          className="clip-corner-sm inline-flex items-center gap-2 bg-[#FF4655] text-white text-xs font-semibold px-3 py-1.5 hover:bg-[#CC3542] transition mt-1">
          Upgrade for unlimited →
        </Link>
      </div>

    </div>
  )
}
