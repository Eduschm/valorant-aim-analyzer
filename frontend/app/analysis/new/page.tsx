import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import { AnalysisForm } from '@/components/analysis/AnalysisForm'

export default function NewAnalysisPage() {
  return (
    <div className="min-h-screen bg-[#0A0B0F]">
      <nav className="border-b border-[#1F2130] px-6 h-14 flex items-center justify-between">
        <Link href="/" className="font-display text-lg font-bold tracking-widest text-[#FF4655] uppercase">
          AimLab<span className="text-[#F0F1F5]">VAL</span>
        </Link>
        <Link href="/auth/signin" className="text-[#42495A] text-xs hover:text-[#F0F1F5] transition">
          Sign in
        </Link>
      </nav>

      <div className="max-w-lg mx-auto px-6 pt-16 pb-24">
        <Link href="/" className="inline-flex items-center gap-2 text-[#42495A] text-sm hover:text-[#F0F1F5] transition mb-10">
          <ArrowLeft className="w-4 h-4" /> Back
        </Link>

        <h1 className="font-display text-4xl font-bold tracking-tight mb-2">
          New Analysis
        </h1>
        <p className="text-[#7A8496] text-sm mb-10">
          Enter a Riot ID to analyze the last 20 matches.
        </p>

        <AnalysisForm />
      </div>
    </div>
  )
}
