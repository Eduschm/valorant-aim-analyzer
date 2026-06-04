'use client'

import { TrendingUp, Target, Zap } from 'lucide-react'

export function QuickStats() {
  const recentStats = {
    averageHS: 42.8,
    averageADR: 156.4,
    analysesThisMonth: 12,
  }

  return (
    <div className="grid md:grid-cols-3 gap-4">
      <div className="bg-surface-500 border border-secondary-700 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-secondary-400 text-sm mb-1">Average HS%</p>
            <p className="text-3xl font-bold text-accent-400">{recentStats.averageHS}%</p>
          </div>
          <Target className="w-12 h-12 text-accent-400 opacity-20" />
        </div>
      </div>

      <div className="bg-surface-500 border border-secondary-700 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-secondary-400 text-sm mb-1">Average ADR</p>
            <p className="text-3xl font-bold text-primary-400">{recentStats.averageADR}</p>
          </div>
          <Zap className="w-12 h-12 text-primary-400 opacity-20" />
        </div>
      </div>

      <div className="bg-surface-500 border border-secondary-700 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-secondary-400 text-sm mb-1">Analyses This Month</p>
            <p className="text-3xl font-bold text-accent-400">{recentStats.analysesThisMonth}</p>
          </div>
          <TrendingUp className="w-12 h-12 text-accent-400 opacity-20" />
        </div>
      </div>
    </div>
  )
}
