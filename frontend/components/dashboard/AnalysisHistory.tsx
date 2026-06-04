'use client'

import Link from 'next/link'
import { mockAnalysisHistory } from '@/lib/mock/analysis'
import { ArrowRight } from 'lucide-react'

function formatDate(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

export function AnalysisHistory() {
  return (
    <div className="bg-surface-500 border border-secondary-700 rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-secondary-700 bg-secondary-600/50">
              <th className="px-6 py-4 text-left text-secondary-300 font-semibold">Date</th>
              <th className="px-6 py-4 text-left text-secondary-300 font-semibold">Riot ID</th>
              <th className="px-6 py-4 text-left text-secondary-300 font-semibold">HS%</th>
              <th className="px-6 py-4 text-left text-secondary-300 font-semibold">ADR</th>
              <th className="px-6 py-4 text-left text-secondary-300 font-semibold">Status</th>
              <th className="px-6 py-4 text-right text-secondary-300 font-semibold">Action</th>
            </tr>
          </thead>
          <tbody>
            {mockAnalysisHistory.map((analysis, idx) => (
              <tr key={idx} className="border-b border-secondary-700 hover:bg-secondary-600/30 transition">
                <td className="px-6 py-4 text-secondary-100">
                  {formatDate(analysis.createdAt)}
                </td>
                <td className="px-6 py-4 text-secondary-100">{analysis.riotId}</td>
                <td className="px-6 py-4 text-accent-400 font-semibold">{analysis.stats.headshotPercent}%</td>
                <td className="px-6 py-4 text-accent-400 font-semibold">{analysis.stats.adr.toFixed(1)}</td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-semibold">
                    ● Completed
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <Link href={`/analysis/${analysis.id}`} className="inline-flex items-center gap-1 text-primary-400 hover:text-primary-300 transition">
                    View
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
