'use client'

import { StatsCards } from './StatsCards'
import { WeaponStats } from './WeaponStats'
import Link from 'next/link'
import { ArrowLeft, Share2, Download } from 'lucide-react'

export function ReportView({ analysis }: { analysis: any }) {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <Link href="/dashboard" className="flex items-center gap-2 text-secondary-300 hover:text-primary-400 transition">
          <ArrowLeft className="w-5 h-5" />
          Back to Dashboard
        </Link>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 bg-secondary-700 text-secondary-100 px-4 py-2 rounded-lg hover:bg-secondary-600 transition">
            <Share2 className="w-5 h-5" />
            Share
          </button>
          <button className="flex items-center gap-2 bg-secondary-700 text-secondary-100 px-4 py-2 rounded-lg hover:bg-secondary-600 transition">
            <Download className="w-5 h-5" />
            Download
          </button>
        </div>
      </div>

      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Aim Analysis Report</h1>
        <p className="text-secondary-300">Riot ID: <span className="text-accent-400 font-semibold">{analysis.riotId}</span></p>
      </div>

      {/* Stats Cards */}
      <StatsCards stats={analysis.stats} />

      {/* Weapon Stats */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Weapon Performance</h2>
        <WeaponStats data={analysis.weaponStats} />
      </div>

      {/* Coaching Report */}
      <div className="mt-8 bg-surface-500 border border-secondary-700 rounded-lg p-8">
        <h2 className="text-2xl font-bold mb-4">Coaching Report</h2>
        <div className="prose prose-invert max-w-none">
          <p className="text-secondary-300 whitespace-pre-wrap">{analysis.coachingReport}</p>
        </div>
      </div>
    </div>
  )
}
