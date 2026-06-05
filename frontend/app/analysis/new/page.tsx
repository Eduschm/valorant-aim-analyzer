import Link from 'next/link'
import { ArrowLeft, Crosshair } from 'lucide-react'
import { AnalysisForm } from '@/components/analysis/AnalysisForm'
import { Reveal } from '@/components/ui/motion'

export default function NewAnalysisPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#07080C]">
      <div className="pointer-events-none absolute inset-0 bg-radial-glow" />
      <div className="pointer-events-none absolute inset-0 bg-grid aurora" />

      <nav className="relative flex h-14 items-center justify-between border-b border-[#1F2130] px-6">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center clip-corner-sm bg-gradient-to-br from-[#FF4655] to-[#B8323D]">
            <Crosshair className="h-4 w-4 text-white" />
          </span>
          <span className="font-display text-lg font-bold uppercase tracking-widest">
            <span className="text-[#FF4655]">AimLab</span>
            <span className="text-[#F0F1F5]">VAL</span>
          </span>
        </Link>
        <Link href="/auth/signin" className="text-xs text-[#42495A] transition hover:text-[#F0F1F5]">
          Sign in
        </Link>
      </nav>

      <div className="relative mx-auto max-w-lg px-6 pb-24 pt-16">
        <Reveal>
          <Link
            href="/"
            className="mb-10 inline-flex items-center gap-2 text-sm text-[#42495A] transition hover:text-[#F0F1F5]"
          >
            <ArrowLeft className="h-4 w-4" /> Back
          </Link>

          <p className="mb-2 text-xs uppercase tracking-[0.3em] text-[#FF4655]">Step 1 of 1</p>
          <h1 className="font-display text-4xl font-bold tracking-tight">New Analysis</h1>
          <p className="mb-10 mt-2 text-sm text-[#7A8496]">
            Enter a Riot ID to analyze the last 20 matches.
          </p>
        </Reveal>

        <Reveal delay={0.1}>
          <div className="glass rounded-2xl p-7">
            <AnalysisForm />
          </div>
        </Reveal>
      </div>
    </div>
  )
}
