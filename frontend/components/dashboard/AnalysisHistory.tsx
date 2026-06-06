'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { getAllAnalyses } from '@/lib/storage'
import { mockAnalysisHistory } from '@/lib/mock/analysis'

function timeAgo(iso: string) {
  const ms = Date.now() - new Date(iso).getTime()
  const m  = Math.floor(ms / 60000)
  const h  = Math.floor(ms / 3600000)
  const d  = Math.floor(ms / 86400000)
  if (m < 60)  return `${m}m ago`
  if (h < 24)  return `${h}h ago`
  if (d < 7)   return `${d}d ago`
  return new Date(iso).toLocaleDateString()
}

const MOCK_MODE = process.env.NEXT_PUBLIC_MOCK_MODE === 'true'

export function AnalysisHistory() {
  const [rows, setRows] = useState<any[]>([])

  useEffect(() => {
    if (MOCK_MODE) {
      setRows(mockAnalysisHistory)
      return
    }
    const stored = getAllAnalyses().map(a => ({
      id:        a.id,
      riotId:    a.riot_id,
      createdAt: a.saved_at,
      status:    'completed',
      stats: {
        headshotPercent: a.riot_report?.avg_headshot_pct ?? 0,
        adr:             a.riot_report?.avg_adr ?? 0,
      },
    }))
    setRows(stored.length > 0 ? stored : mockAnalysisHistory)
  }, [])

  if (rows.length === 0) {
    return (
      <div className="glass rounded-xl p-10 text-center text-sm text-[#42495A]">
        No analyses yet.{' '}
        <Link href="/analysis/new" className="text-val-accent hover:underline">
          Run your first one
        </Link>
      </div>
    )
  }

  return (
    <div className="glass overflow-hidden rounded-xl">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-[#1F2130]">
            {['Date', 'Riot ID', 'HS%', 'ADR', 'Status', ''].map(h => (
              <th key={h} className="px-5 py-3 text-left text-xs font-medium uppercase tracking-widest text-[#42495A]">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-[#1F2130] transition last:border-0 hover:bg-white/[0.02]">
              <td className="px-5 py-3 text-[#7A8496]">{timeAgo(row.createdAt)}</td>
              <td className="px-5 py-3 font-mono text-[#F0F1F5]">{row.riotId}</td>
              <td className="px-5 py-3 text-[#F0F1F5]">{row.stats.headshotPercent.toFixed(1)}%</td>
              <td className="px-5 py-3 text-[#F0F1F5]">{row.stats.adr.toFixed(0)}</td>
              <td className="px-5 py-3">
                <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-xs text-emerald-400">Done</span>
              </td>
              <td className="px-5 py-3 text-right">
                <Link href={`/analysis/${row.id}`} className="inline-flex items-center gap-1 text-xs text-val-accent hover:underline">
                  View <ArrowRight className="h-3 w-3" />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
