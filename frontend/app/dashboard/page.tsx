'use client'

import { AnalysisHistory } from '@/components/dashboard/AnalysisHistory'
import { QuickStats } from '@/components/dashboard/QuickStats'
import Link from 'next/link'
import { Plus } from 'lucide-react'

export default function DashboardPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-secondary-300 mt-2">Track your aim improvement over time</p>
          </div>
          <Link href="/analysis/new" className="inline-flex items-center gap-2 bg-primary-400 text-secondary-900 px-4 py-2 rounded-lg font-semibold hover:bg-primary-500 transition">
            <Plus className="w-5 h-5" />
            New Analysis
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <QuickStats />

      {/* Analysis History */}
      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">Recent Analyses</h2>
        <AnalysisHistory />
      </div>
    </div>
  )
}
