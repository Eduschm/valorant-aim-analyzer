'use client'

import { useEffect, useState } from 'react'
import { Target, Swords, Activity } from 'lucide-react'
import { getAllAnalyses } from '@/lib/storage'

export function QuickStats() {
  const [stats, setStats] = useState({ avgHS: 0, avgADR: 0, count: 0 })

  useEffect(() => {
    const analyses = getAllAnalyses()
    if (analyses.length === 0) {
      setStats({ avgHS: 0, avgADR: 0, count: 0 })
      return
    }
    const valid = analyses.filter(a => a.riot_report)
    const avgHS  = valid.reduce((s, a) => s + (a.riot_report?.avg_headshot_pct ?? 0), 0) / (valid.length || 1)
    const avgADR = valid.reduce((s, a) => s + (a.riot_report?.avg_adr ?? 0), 0)          / (valid.length || 1)
    setStats({ avgHS, avgADR, count: analyses.length })
  }, [])

  const cards = [
    { label: 'Avg HS%',        value: stats.avgHS  ? `${stats.avgHS.toFixed(1)}%`  : '—', icon: Target   },
    { label: 'Avg ADR',        value: stats.avgADR ? stats.avgADR.toFixed(0)        : '—', icon: Swords   },
    { label: 'Analyses saved', value: stats.count  ? String(stats.count)            : '0', icon: Activity },
  ]

  return (
    <div className="grid grid-cols-3 gap-px bg-[#1F2130]">
      {cards.map(({ label, value, icon: Icon }) => (
        <div key={label} className="bg-[#111318] p-5">
          <div className="flex items-center gap-2 text-[#42495A] text-xs uppercase tracking-widest mb-2">
            <Icon className="w-3 h-3" /> {label}
          </div>
          <div className="font-display text-3xl font-bold text-[#F0F1F5]">{value}</div>
        </div>
      ))}
    </div>
  )
}
