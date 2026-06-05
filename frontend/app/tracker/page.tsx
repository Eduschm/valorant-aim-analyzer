'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { StatsTrend } from '@/components/tracker/StatsTrend'
import { MatchTable } from '@/components/tracker/MatchTable'
import { getAllAnalyses, getAnalyses, StoredAnalysis } from '@/lib/storage'
import { MOCK_REPORT } from '@/lib/mock/analysis'

export default function TrackerPage() {
  const params  = useSearchParams()
  const riotId  = params.get('id') || ''

  const [analyses, setAnalyses] = useState<StoredAnalysis[]>([])
  const [latest,   setLatest]   = useState<StoredAnalysis | null>(null)

  useEffect(() => {
    const all   = riotId ? getAnalyses(riotId) : getAllAnalyses()
    // Use mock if nothing stored yet
    if (all.length === 0) {
      const mock: StoredAnalysis = {
        id: 'mock-001', riot_id: 'DemoPlayer#NA1', saved_at: new Date().toISOString(),
        riot_report: MOCK_REPORT.riot_report as any,
        coaching:    MOCK_REPORT.coaching   as any,
      }
      setAnalyses([mock])
      setLatest(mock)
    } else {
      setAnalyses(all)
      setLatest(all[0])
    }
  }, [riotId])

  const current = latest?.riot_report
  const prev    = analyses[1]?.riot_report ?? null

  // Build rank history for chart (newest last for left-to-right)
  const chartData = [...analyses].reverse().map((a, i) => ({
    label: `#${i + 1}`,
    hs:    a.riot_report?.avg_headshot_pct ?? 0,
    adr:   a.riot_report?.avg_adr ?? 0,
  }))

  const matches = current?.matches ?? []

  return (
    <div className="p-8 max-w-5xl space-y-8 fade-in">

      {/* Header */}
      <div>
        <p className="text-xs uppercase tracking-widest text-[#42495A] mb-2">Tracker</p>
        <div className="flex items-baseline gap-3">
          <h1 className="font-display text-3xl font-bold tracking-tight">
            {current?.game_name ?? '—'}<span className="text-[#42495A] text-xl">#{current?.tag_line}</span>
          </h1>
          {current?.current_rank && (
            <span className="text-[#FF4655] text-sm font-semibold">{current.current_rank}</span>
          )}
          {current?.rank_delta !== undefined && (
            <span className={`text-xs ${current.rank_delta >= 0 ? 'text-green-400' : 'text-[#FF4655]'}`}>
              {current.rank_delta >= 0 ? '+' : ''}{current.rank_delta} tiers
            </span>
          )}
        </div>
        {!riotId && (
          <p className="text-[#42495A] text-xs mt-1">
            Showing latest analysis. <Link href="/analysis/new" className="text-[#FF4655] hover:underline">Run a new one →</Link>
          </p>
        )}
      </div>

      {/* Trend charts */}
      {chartData.length > 1 && (
        <div className="border border-[#1F2130] bg-[#111318] p-5">
          <p className="text-xs uppercase tracking-widest text-[#42495A] mb-4">HS% over analyses</p>
          <ResponsiveContainer width="100%" height={120}>
            <LineChart data={chartData}>
              <XAxis dataKey="label" tick={{ fill: '#42495A', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis domain={['auto', 'auto']} tick={{ fill: '#42495A', fontSize: 11 }} axisLine={false} tickLine={false} width={30} />
              <Tooltip
                contentStyle={{ background: '#111318', border: '1px solid #1F2130', borderRadius: 0, fontSize: 12 }}
                labelStyle={{ color: '#7A8496' }}
                itemStyle={{ color: '#FF4655' }}
              />
              <Line type="monotone" dataKey="hs" stroke="#FF4655" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Stats trends */}
      <div className="grid grid-cols-3 gap-px bg-[#1F2130]">
        <StatsTrend
          label="Headshot %"
          current={current?.avg_headshot_pct ?? 0}
          prev={prev?.avg_headshot_pct ?? null}
          format={v => `${v.toFixed(1)}%`}
        />
        <StatsTrend
          label="Avg ADR"
          current={current?.avg_adr ?? 0}
          prev={prev?.avg_adr ?? null}
          format={v => v.toFixed(0)}
        />
        <StatsTrend
          label="Win rate"
          current={(current?.win_rate ?? 0) * 100}
          prev={prev ? (prev.win_rate ?? 0) * 100 : null}
          format={v => `${v.toFixed(0)}%`}
        />
      </div>

      {/* Match log */}
      <div>
        <p className="text-xs uppercase tracking-widest text-[#42495A] mb-3">
          Match log ({matches.length} matches)
        </p>
        {matches.length > 0
          ? <MatchTable matches={matches} />
          : <p className="text-[#42495A] text-sm border border-[#1F2130] bg-[#111318] p-6 text-center">No match data. Run an analysis first.</p>
        }
      </div>

    </div>
  )
}
