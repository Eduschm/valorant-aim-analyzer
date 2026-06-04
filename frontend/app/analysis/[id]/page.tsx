'use client'

import { useParams } from 'next/navigation'
import { ReportView } from '@/components/analysis/ReportView'
import { mockAnalysis } from '@/lib/mock/analysis'

export default function AnalysisReportPage() {
  const params = useParams()
  const id = params.id as string

  // In a real app, fetch from API based on id
  // For now, use mock data
  const analysis = mockAnalysis

  return (
    <div className="min-h-screen bg-secondary-900 p-8">
      <ReportView analysis={analysis} />
    </div>
  )
}
