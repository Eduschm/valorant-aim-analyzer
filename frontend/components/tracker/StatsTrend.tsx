'use client'

import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface StatsTrendProps {
  label:   string
  current: number
  prev:    number | null
  format:  (v: number) => string
}

export function StatsTrend({ label, current, prev, format }: StatsTrendProps) {
  const delta  = prev !== null ? current - prev : null
  const pctChg = prev && prev !== 0 ? ((current - prev) / prev) * 100 : null

  const up = delta !== null && delta > 0
  const dn = delta !== null && delta < 0

  return (
    <div className="bg-val-surface border border-val-border p-5">
      <p className="text-xs uppercase tracking-widest text-val-muted mb-3">{label}</p>
      <p className="font-display text-4xl font-bold text-val-text mb-2">{format(current)}</p>
      {delta !== null ? (
        <div className={`flex items-center gap-1 text-xs ${up ? 'text-val-green' : dn ? 'text-val-red' : 'text-val-muted'}`}>
          {up ? <TrendingUp className="w-3 h-3" /> : dn ? <TrendingDown className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
          {up ? '+' : ''}{format(delta)} vs last analysis
          {pctChg !== null && <span className="text-val-muted ml-1">({pctChg > 0 ? '+' : ''}{pctChg.toFixed(1)}%)</span>}
        </div>
      ) : (
        <p className="text-val-muted text-xs">First analysis</p>
      )}
    </div>
  )
}
