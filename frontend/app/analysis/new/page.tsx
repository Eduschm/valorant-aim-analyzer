'use client'

import { AnalysisForm } from '@/components/analysis/AnalysisForm'

export default function NewAnalysisPage() {
  return (
    <div className="min-h-screen bg-secondary-900">
      <div className="max-w-2xl mx-auto p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">New Analysis</h1>
          <p className="text-secondary-300 mt-2">Enter a Valorant player ID to analyze their last 20 matches</p>
        </div>

        <AnalysisForm />
      </div>
    </div>
  )
}
