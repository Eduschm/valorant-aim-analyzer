'use client'

import { BarChart3, Crosshair, TrendingUp, Target } from 'lucide-react'

export function StatsCards({ stats }: { stats: any }) {
  const cards = [
    {
      icon: Crosshair,
      label: 'Headshot %',
      value: `${stats.headshotPercent}%`,
      color: 'bg-primary-400',
    },
    {
      icon: BarChart3,
      label: 'Average Damage/Round',
      value: stats.adr.toFixed(1),
      color: 'bg-accent-400',
    },
    {
      icon: TrendingUp,
      label: 'Rank Delta',
      value: stats.rankDelta,
      color: 'bg-green-500',
    },
    {
      icon: Target,
      label: 'Matches Analyzed',
      value: stats.matchesAnalyzed,
      color: 'bg-purple-500',
    },
  ]

  return (
    <div className="grid md:grid-cols-4 gap-4">
      {cards.map((card, idx) => {
        const Icon = card.icon
        return (
          <div key={idx} className="bg-surface-500 border border-secondary-700 rounded-lg p-6">
            <div className={`w-12 h-12 ${card.color} rounded-lg p-3 mb-4`}>
              <Icon className="w-full h-full text-white" />
            </div>
            <p className="text-secondary-400 text-sm mb-1">{card.label}</p>
            <p className="text-3xl font-bold text-secondary-100">{card.value}</p>
          </div>
        )
      })}
    </div>
  )
}
