'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { getAllAnalyses, StoredAnalysis } from '@/lib/storage'
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
      <div className="border border-val-border bg-val-surface p-10 text-center text-val-muted text-sm">
        No analyses yet.{' '}
        <Link href="/analysis/new" className="text-val-red hover:underline">Run your first one →</Link>
      </div>
    )
  }

  return (
    <div className="border border-val-border bg-val-surface overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-val-border">
            {['Date', 'Riot ID', 'HS%', 'ADR', 'Status', ''].map(h => (
              <th key={h} className="px-5 py-3 text-left text-val-muted text-xs uppercase tracking-widest font-medium">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-val-border last:border-0 hover:bg-val-surface-2 transition">
              <td className="px-5 py-3 text-val-subtle">{timeAgo(row.createdAt)}</td>
              <td className="px-5 py-3 text-val-text font-mono">{row.riotId}</td>
              <td className="px-5 py-3 text-val-text">{row.stats.headshotPercent.toFixed(1)}%</td>
              <td className="px-5 py-3 text-val-text">{row.stats.adr.toFixed(0)}</td>
              <td className="px-5 py-3">
                <span className="text-xs text-val-green bg-val-green-dim px-2 py-0.5">Done</span>
              </td>
              <td className="px-5 py-3 text-right">
                <Link href={`/analysis/${row.id}`} className="inline-flex items-center gap-1 text-val-red text-xs hover:underline">
                  View <ArrowRight className="w-3 h-3" />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
