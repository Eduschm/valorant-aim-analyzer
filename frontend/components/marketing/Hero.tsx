'use client'

import { motion } from 'framer-motion'
import { easeOut } from '@/components/ui/motion'
import { AnalysisForm } from '@/components/analysis/AnalysisForm'
import { AimVisualizer } from './AimVisualizer'

/**
 * Landing hero. The Riot ID form is on the left, and the interactive 
 * aim simulator is on the right.
 */
export function Hero() {
  return (
    <section id="analyze" className="relative mx-auto max-w-6xl px-6 pt-32 pb-16">
      <div className="grid items-center gap-12 lg:grid-cols-12">
        {/* Copy & Form (Left Column) */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: easeOut }}
          className="lg:col-span-6 space-y-8"
        >
          <div>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#1F2130] bg-[#111318]/60 px-4 py-1.5 text-[10px] uppercase tracking-widest text-[#7A8496]">
              <span className="h-1.5 w-1.5 rounded-full bg-val-accent pulse-red" />
              AI coaching · Riot data · Free to start
            </div>

            <h1 className="font-display text-4xl sm:text-5xl font-bold leading-[1.05] tracking-tight md:text-6xl text-[#F0F1F5]">
              Understand why you
              <br />
              <span className="gradient-text text-glow">lose gunfights.</span>
            </h1>

            <p className="mt-6 text-base leading-relaxed text-[#7A8496]">
              Paste your Riot ID. We pull your last 20 matches, analyze your aim patterns, and give
              you a direct coaching report with specific numbers and specific fixes.
            </p>
          </div>

          <div className="glass rounded-xl p-6 border border-white/5 relative overflow-hidden shadow-accent-glow-sm">
            <div className="pointer-events-none absolute inset-0 bg-grid opacity-20" />
            <div className="relative">
              <p className="mb-1 text-[10px] uppercase tracking-[0.2em] text-val-accent font-bold">Start Free Analysis</p>
              <h2 className="mb-4 font-display text-xl font-bold tracking-tight text-[#F0F1F5]">Analyze your aim</h2>
              <AnalysisForm />
            </div>
          </div>
        </motion.div>

        {/* Interactive Aim Simulator (Right Column) */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1, ease: easeOut }}
          className="lg:col-span-6 w-full"
        >
          <div className="relative">
            <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-val-accent/20 to-purple-500/20 blur-xl opacity-70" />
            <div className="relative">
              <AimVisualizer />
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

