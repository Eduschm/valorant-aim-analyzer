'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowLeft, TrendingUp, Target, Swords, Trophy, AlertCircle, Crosshair, Sparkles } from 'lucide-react'
import { saveAnalysis } from '@/lib/storage'
import { logger } from '@/lib/logger'
import { Stagger, Item, Reveal } from '@/components/ui/motion'
import { AnimatedCounter } from '@/components/ui/AnimatedCounter'
import { AgentIcon } from '@/components/ui/AgentIcon'
import { RankBadge } from '@/components/ui/RankBadge'
import { Celebrate } from '@/components/ui/Celebrate'

interface Report {
  report_id: string
  status: string
  riot_report: any
  cv_report:   any
  coaching:    any
  error:       string | null
}

const POLL_MS      = 3000
const POLL_TIMEOUT = 90_000  // give up after 90s

const MISTAKE_COLORS: Record<string, string> = {
  overshoot:             'bg-red-500',
  undershoot:            'bg-orange-500',
  body_not_head:         'bg-yellow-500',
  wrong_target:          'bg-pink-500',
  moving_while_shooting: 'bg-blue-400',
  spray_control:         'bg-purple-500',
}

export default function AnalysisReportPage() {
  const params = useParams()
  const id = params.id as string

  const [report, setReport] = useState<Report | null>(null)
  const [loadingMsg, setLoadingMsg] = useState('Fetching match history...')
  const [error, setError] = useState('')

  // Cycle loading messages while processing
  useEffect(() => {
    const msgs = ['Fetching match history...', 'Parsing match stats...', 'Generating coaching report...', 'Almost done...']
    let i = 0
    const interval = setInterval(() => { i = (i + 1) % msgs.length; setLoadingMsg(msgs[i]) }, 3500)
    return () => clearInterval(interval)
  }, [])

  // Poll until done
  useEffect(() => {
    let cancelled = false
    const startedAt = Date.now()

    const poll = async () => {
      // Hard timeout, surface an error instead of spinning forever
      if (Date.now() - startedAt > POLL_TIMEOUT) {
        if (!cancelled) setError('Analysis timed out. Check that RIOT_API_KEY and ANTHROPIC_API_KEY are set in .env, then try again.')
        return
      }

      try {
        const res = await fetch(`/api/analysis/${id}`)
        if (!res.ok) throw new Error(`${res.status}`)
        const json = await res.json()
        if (typeof json === 'object' && json !== null && 'success' in json && json.success === false) {
          throw new Error(json.error || 'Failed to load report')
        }

        const data: Report = json.data || json

        if (!cancelled) {
          setReport(data)
          if (data.status === 'done' && data.riot_report) {
            saveAnalysis(data)
          }
          if (data.status !== 'done' && data.status !== 'error') {
            setTimeout(poll, POLL_MS)
          }
        }
      } catch (e: any) {
        logger.error('Polling report failed', id, e)
        if (!cancelled) setError(e.message || 'Could not load report. Is the API running?')
      }
    }

    poll()
    return () => { cancelled = true }
  }, [id])

  // --- Error ---
  if (error || report?.status === 'error') {
    const errorMessage = report?.status === 'error' ? report.error || 'Unknown error' : error
    return (
      <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#070B18] px-4">
        <div className="pointer-events-none absolute inset-0 bg-radial-glow" />
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="glass relative max-w-md rounded-2xl p-10 text-center"
        >
          <AlertCircle className="mx-auto mb-4 h-10 w-10 text-val-danger" />
          <h2 className="mb-2 text-xl font-bold">Analysis failed</h2>
          <p className="text-sm text-[#7A8496]">{errorMessage}</p>
          <Link
            href="/analysis/new"
            className="clip-corner-sm mt-6 inline-block bg-val-accent px-5 py-2 text-sm font-semibold text-white transition hover:bg-val-accent-dark"
          >
            Try again
          </Link>
        </motion.div>
      </div>
    )
  }

  // --- Loading ---
  if (!report || report.status !== 'done') {
    return (
      <div className="relative flex min-h-screen flex-col items-center justify-center gap-6 overflow-hidden bg-[#070B18]">
        <div className="pointer-events-none absolute inset-0 bg-radial-glow" />
        <div className="pointer-events-none absolute inset-0 bg-grid aurora" />
        <div className="relative">
          <div className="h-14 w-14 animate-spin rounded-full border-2 border-[#1F2130] border-t-val-accent" />
          <Crosshair className="absolute left-1/2 top-1/2 h-5 w-5 -translate-x-1/2 -translate-y-1/2 text-val-accent" />
        </div>
        <motion.p
          key={loadingMsg}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative text-sm text-[#7A8496]"
        >
          {loadingMsg}
        </motion.p>
      </div>
    )
  }

  const riot     = report.riot_report
  const coaching = report.coaching

  const statCards = [
    { label: 'Headshot %', value: riot?.avg_headshot_pct ?? 0, decimals: 1, suffix: '%', icon: Target },
    { label: 'Avg ADR',    value: riot?.avg_adr ?? 0,          decimals: 0, suffix: '',  icon: Swords },
    { label: 'Win rate',   value: (riot?.win_rate ?? 0) * 100, decimals: 0, suffix: '%', icon: Trophy },
  ]

  const promoted = (riot?.rank_delta ?? 0) > 0

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#070B18]">
      <div className="pointer-events-none absolute inset-0 bg-radial-glow" />
      <Celebrate trigger={report.status === 'done' && !!riot} intense={promoted} />

      {/* Nav */}
      <nav className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-[#1F2130] bg-[#070B18]/85 px-6 backdrop-blur">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center clip-corner-sm bg-gradient-to-br from-val-accent to-val-accent-dark">
            <Crosshair className="h-4 w-4 text-white" />
          </span>
          <span className="font-display text-lg font-bold uppercase tracking-widest">
            <span className="text-val-accent">AimLab</span>
            <span className="text-[#F0F1F5]">VAL</span>
          </span>
        </Link>
        <div className="flex items-center gap-4">
          <Link href="/tracker" className="text-xs text-[#7A8496] transition hover:text-[#F0F1F5]">
            Tracker
          </Link>
          <Link
            href="/analysis/new"
            className="clip-corner-sm bg-val-accent px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-val-accent-dark"
          >
            New analysis
          </Link>
        </div>
      </nav>

      <div className="relative mx-auto max-w-4xl space-y-8 px-6 py-12">

        {/* Header */}
        <Reveal>
          <Link
            href="/analysis/new"
            className="mb-4 inline-flex items-center gap-1 text-xs text-[#42495A] transition hover:text-[#F0F1F5]"
          >
            <ArrowLeft className="h-3 w-3" /> New analysis
          </Link>
          <div className="flex items-center gap-5">
            <RankBadge rank={riot?.current_rank || 'Unranked'} size={72} promoted={promoted} />
            <div>
              <h1 className="font-display text-4xl font-bold tracking-tight">
                {riot?.game_name}
                <span className="text-[#42495A]">#{riot?.tag_line}</span>
              </h1>
              <div className="mt-3 flex flex-wrap items-center gap-3 text-sm text-[#7A8496]">
                <span className="inline-flex items-center gap-1.5 rounded-full border border-val-accent/30 bg-val-accent/10 px-3 py-1 font-semibold text-val-accent">
                  {riot?.current_rank || 'Unranked'}
                </span>
                <span>{riot?.matches?.length || 0} matches</span>
                <span className="text-[#42495A]">·</span>
                <span className={riot?.rank_delta >= 0 ? 'text-emerald-400' : 'text-val-danger'}>
                  {riot?.rank_delta >= 0 ? '+' : ''}{riot?.rank_delta} tiers
                </span>
              </div>
            </div>
          </div>
        </Reveal>

        {/* Stats row */}
        <Stagger className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {statCards.map(({ label, value, decimals, suffix, icon: Icon }) => (
            <Item key={label}>
              <div className="glass glass-hover h-full rounded-xl p-5">
                <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-widest text-[#42495A]">
                  <Icon className="h-3.5 w-3.5 text-val-accent" /> {label}
                </div>
                <div className="font-display text-3xl font-bold text-[#F0F1F5]">
                  <AnimatedCounter value={value} decimals={decimals} suffix={suffix} />
                </div>
              </div>
            </Item>
          ))}
          <Item>
            <div className="glass glass-hover h-full rounded-xl p-5">
              <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-widest text-[#42495A]">
                <TrendingUp className="h-3.5 w-3.5 text-val-accent" /> Top agent
              </div>
              <div className="flex items-center gap-2.5">
                <AgentIcon name={riot?.top_agent} size={36} />
                <span className="font-display text-2xl font-bold text-[#F0F1F5]">{riot?.top_agent ?? '-'}</span>
              </div>
            </div>
          </Item>
        </Stagger>

        {/* AI Coaching */}
        {coaching && (
          <Reveal>
            <div className="glass overflow-hidden rounded-xl">
              <div className="flex items-center gap-2 border-b border-[#1F2130] px-6 py-4">
                <Sparkles className="h-4 w-4 text-val-accent" />
                <span className="text-xs uppercase tracking-widest text-[#7A8496]">AI Coaching Report</span>
              </div>
              <div className="space-y-6 p-6">
                <p className="leading-relaxed text-[#F0F1F5]">{coaching.summary}</p>

                {coaching.top_weakness && (
                  <div className="border-l-2 border-val-accent pl-4">
                    <p className="mb-1 text-xs uppercase tracking-widest text-[#42495A]">Top weakness</p>
                    <p className="font-semibold text-val-accent">{coaching.top_weakness}</p>
                  </div>
                )}

                {coaching.tips?.length > 0 && (
                  <div>
                    <p className="mb-3 text-xs uppercase tracking-widest text-[#42495A]">Actionable tips</p>
                    <ol className="space-y-3">
                      {coaching.tips.map((tip: string, i: number) => (
                        <motion.li
                          key={i}
                          initial={{ opacity: 0, x: -8 }}
                          whileInView={{ opacity: 1, x: 0 }}
                          viewport={{ once: true }}
                          transition={{ delay: i * 0.06 }}
                          className="flex gap-3 text-sm leading-relaxed text-[#7A8496]"
                        >
                          <span className="w-5 flex-shrink-0 font-display font-bold text-val-accent">{i + 1}.</span>
                          {tip}
                        </motion.li>
                      ))}
                    </ol>
                  </div>
                )}

                {coaching.encouragement && (
                  <p className="border-t border-[#1F2130] pt-4 text-sm italic text-[#7A8496]">
                    {coaching.encouragement}
                  </p>
                )}
              </div>
            </div>
          </Reveal>
        )}

        {/* CV report (Phase 2) */}
        {report.cv_report && (
          <Reveal>
            <div className="glass overflow-hidden rounded-xl">
              <div className="flex items-center gap-2 border-b border-[#1F2130] px-6 py-4">
                <div className="h-1.5 w-1.5 rounded-full bg-val-accent" />
                <span className="text-xs uppercase tracking-widest text-[#7A8496]">Clip Analysis</span>
              </div>
              <div className="space-y-4 p-6">
                <div className="grid grid-cols-2 gap-4 text-sm md:grid-cols-3">
                  <div>
                    <p className="mb-1 text-xs uppercase tracking-widest text-[#42495A]">Engagements</p>
                    <p className="font-display text-2xl font-bold">{report.cv_report.total_engagements}</p>
                  </div>
                  <div>
                    <p className="mb-1 text-xs uppercase tracking-widest text-[#42495A]">Mistakes/min</p>
                    <p className="font-display text-2xl font-bold">{report.cv_report.mistakes_per_minute}</p>
                  </div>
                  <div>
                    <p className="mb-1 text-xs uppercase tracking-widest text-[#42495A]">Most impactful</p>
                    <p className="font-bold text-val-accent">{report.cv_report.most_impactful || '-'}</p>
                  </div>
                </div>

                {report.cv_report.ranked_mistakes?.length > 0 && (
                  <div className="space-y-2 pt-2">
                    {report.cv_report.ranked_mistakes.map((r: any) => (
                      <div key={r.mistake} className="flex items-center gap-3 text-sm">
                        <span className="w-4 text-right text-xs text-[#42495A]">{r.rank}.</span>
                        <span className="w-40 text-[#7A8496]">{r.label}</span>
                        <div className="h-1.5 flex-1 rounded-full bg-[#1F2130]">
                          <motion.div
                            className={`h-1.5 rounded-full ${MISTAKE_COLORS[r.mistake] ?? 'bg-val-accent'}`}
                            initial={{ width: 0 }}
                            whileInView={{ width: r.share_of_total }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.9, ease: 'easeOut' }}
                          />
                        </div>
                        <span className="w-12 text-right text-xs text-[#42495A]">{r.share_of_total}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </Reveal>
        )}

        {/* Match history */}
        {riot?.matches?.length > 0 && (
          <Reveal>
            <div className="glass overflow-hidden rounded-xl">
              <div className="flex items-center gap-2 border-b border-[#1F2130] px-6 py-4">
                <div className="h-1.5 w-1.5 rounded-full bg-val-accent" />
                <span className="text-xs uppercase tracking-widest text-[#7A8496]">Recent matches</span>
              </div>
              <div className="divide-y divide-[#1F2130]">
                {riot.matches.slice(0, 8).map((m: any, i: number) => (
                  <div key={i} className="flex items-center gap-4 px-6 py-3 text-sm transition hover:bg-white/[0.02]">
                    <span className={`w-4 text-xs font-bold ${m.won ? 'text-emerald-400' : 'text-val-danger'}`}>
                      {m.won ? 'W' : 'L'}
                    </span>
                    <span className="flex w-28 items-center gap-2 truncate text-[#7A8496]">
                      <AgentIcon name={m.agent} size={24} />
                      {m.agent}
                    </span>
                    <span className="font-mono text-[#F0F1F5]">{m.kills}/{m.deaths}/{m.assists}</span>
                    <span className="ml-auto text-[#42495A]">{m.headshot_pct?.toFixed(0)}% HS</span>
                    <span className="w-16 text-right text-[#42495A]">{m.adr?.toFixed(0)} ADR</span>
                  </div>
                ))}
              </div>
            </div>
          </Reveal>
        )}

      </div>
    </div>
  )
}
