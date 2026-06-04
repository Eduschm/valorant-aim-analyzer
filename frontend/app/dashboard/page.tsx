import Link from 'next/link'
import { Plus } from 'lucide-react'
import { AnalysisHistory } from '@/components/dashboard/AnalysisHistory'
import { QuickStats } from '@/components/dashboard/QuickStats'

export default function DashboardPage() {
  return (
    <div className="p-8 max-w-5xl">

      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-val-subtle text-sm mt-1">Your aim analysis history</p>
        </div>
        <Link href="/analysis/new"
          className="clip-corner-sm inline-flex items-center gap-2 bg-val-red text-white text-sm font-semibold px-4 py-2 hover:bg-val-red-dark transition">
          <Plus className="w-4 h-4" /> New Analysis
        </Link>
      </div>

      <QuickStats />

      <div className="mt-8">
        <p className="text-xs uppercase tracking-widest text-val-muted mb-3">Recent analyses</p>
        <AnalysisHistory />
      </div>

    </div>
  )
}
