import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import { AnalysisForm } from '@/components/analysis/AnalysisForm'

export default function NewAnalysisPage() {
  return (
    <div className="min-h-screen bg-val-bg">
      <nav className="border-b border-val-border px-6 h-14 flex items-center justify-between">
        <Link href="/" className="font-display text-lg font-bold tracking-widest text-val-red uppercase">
          AimLab<span className="text-val-text">VAL</span>
        </Link>
        <Link href="/auth/signin" className="text-val-muted text-xs hover:text-val-text transition">
          Sign in
        </Link>
      </nav>

      <div className="max-w-lg mx-auto px-6 pt-16 pb-24">
        <Link href="/" className="inline-flex items-center gap-2 text-val-muted text-sm hover:text-val-text transition mb-10">
          <ArrowLeft className="w-4 h-4" /> Back
        </Link>

        <h1 className="font-display text-4xl font-bold tracking-tight mb-2">
          New Analysis
        </h1>
        <p className="text-val-subtle text-sm mb-10">
          Enter a Riot ID to analyze the last 20 matches.
        </p>

        <AnalysisForm />
      </div>
    </div>
  )
}
