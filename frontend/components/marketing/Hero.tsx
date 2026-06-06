'use client'

import { motion } from 'framer-motion'
import { easeOut } from '@/components/ui/motion'
import { AnalysisForm } from '@/components/analysis/AnalysisForm'

/**
 * Landing hero. The Riot ID form is embedded directly — no button gate before
 * the input. The `#analyze` id is the scroll target for header "Get started".
 */
export function Hero() {
  return (
    <section id="analyze" className="relative mx-auto max-w-6xl px-6 pt-36 pb-20">
      <div className="grid items-center gap-12 lg:grid-cols-2">
        {/* Copy */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: easeOut }}
        >
          <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-[#1F2130] bg-[#111318]/60 px-4 py-1.5 text-xs uppercase tracking-widest text-[#7A8496]">
            <span className="h-1.5 w-1.5 rounded-full bg-val-accent pulse-red" />
            AI coaching · Riot data · Free to start
          </div>

          <h1 className="font-display text-5xl font-bold leading-[1.05] tracking-tight md:text-6xl">
            Understand why you
            <br />
            <span className="gradient-text text-glow">lose gunfights.</span>
          </h1>

          <p className="mt-6 max-w-xl text-lg leading-relaxed text-[#7A8496]">
            Paste your Riot ID. We pull your last 20 matches, analyse your aim patterns, and give
            you a direct coaching report with specific numbers and specific fixes.
          </p>
        </motion.div>

        {/* Form — directly on the page */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1, ease: easeOut }}
          className="glass rounded-2xl p-7 shadow-accent-glow-sm"
        >
          <p className="mb-1 text-xs uppercase tracking-[0.3em] text-val-accent">Start free</p>
          <h2 className="mb-5 font-display text-2xl font-bold tracking-tight">Analyze your aim</h2>
          <AnalysisForm />
        </motion.div>
      </div>
    </section>
  )
}
