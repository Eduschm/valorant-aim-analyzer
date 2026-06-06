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
    <div className="glass glass-hover rounded-xl p-5">
      <p className="text-xs uppercase tracking-widest text-[#42495A] mb-3">{label}</p>
      <p className="font-display text-4xl font-bold text-[#F0F1F5] mb-2">{format(current)}</p>
      {delta !== null ? (
        <div className={`flex items-center gap-1 text-xs ${up ? 'text-green-400' : dn ? 'text-val-danger' : 'text-[#42495A]'}`}>
          {up ? <TrendingUp className="w-3 h-3" /> : dn ? <TrendingDown className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
          {up ? '+' : ''}{format(delta)} vs last analysis
          {pctChg !== null && <span className="text-[#42495A] ml-1">({pctChg > 0 ? '+' : ''}{pctChg.toFixed(1)}%)</span>}
        </div>
      ) : (
        <p className="text-[#42495A] text-xs">First analysis</p>
      )}
    </div>
  )
}
