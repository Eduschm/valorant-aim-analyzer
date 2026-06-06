'use client'

import { useEffect, useState } from 'react'
import { Target, Swords, Activity } from 'lucide-react'
import { getAllAnalyses } from '@/lib/storage'
import { Stagger, Item } from '@/components/ui/motion'
import { AnimatedCounter } from '@/components/ui/AnimatedCounter'

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
    const avgADR = valid.reduce((s, a) => s + (a.riot_report?.avg_adr ?? 0), 0) / (valid.length || 1)
    setStats({ avgHS, avgADR, count: analyses.length })
  }, [])

  const cards = [
    { label: 'Avg HS%',        value: stats.avgHS,  decimals: 1, suffix: '%', icon: Target },
    { label: 'Avg ADR',        value: stats.avgADR, decimals: 0, suffix: '',  icon: Swords },
    { label: 'Analyses saved', value: stats.count,  decimals: 0, suffix: '',  icon: Activity },
  ]

  return (
    <Stagger className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      {cards.map(({ label, value, decimals, suffix, icon: Icon }) => (
        <Item key={label}>
          <div className="glass glass-hover rounded-xl p-5">
            <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-widest text-[#42495A]">
              <Icon className="h-3.5 w-3.5 text-val-accent" /> {label}
            </div>
            <div className="font-display text-3xl font-bold text-[#F0F1F5]">
              <AnimatedCounter value={value} decimals={decimals} suffix={suffix} />
            </div>
          </div>
        </Item>
      ))}
    </Stagger>
  )
}
