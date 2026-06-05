import Link from 'next/link'
import { Plus } from 'lucide-react'
import { AnalysisHistory } from '@/components/dashboard/AnalysisHistory'
import { QuickStats } from '@/components/dashboard/QuickStats'
import { PageTransition } from '@/components/ui/PageTransition'
import { Reveal } from '@/components/ui/motion'

export default function DashboardPage() {
  return (
    <PageTransition className="mx-auto max-w-5xl p-6 sm:p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <p className="mb-1 text-xs uppercase tracking-[0.3em] text-[#FF4655]">Overview</p>
          <h1 className="font-display text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-[#7A8496]">Your aim analysis history</p>
        </div>
        <Link
          href="/analysis/new"
          className="clip-corner-sm inline-flex items-center gap-2 bg-[#FF4655] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#CC3542]"
        >
          <Plus className="h-4 w-4" /> New Analysis
        </Link>
      </div>

      <QuickStats />

      <Reveal className="mt-10">
        <p className="mb-3 text-xs uppercase tracking-widest text-[#42495A]">Recent analyses</p>
        <AnalysisHistory />
      </Reveal>
    </PageTransition>
  )
}
