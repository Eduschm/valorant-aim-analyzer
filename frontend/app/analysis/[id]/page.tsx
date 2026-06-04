'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, TrendingUp, Target, Swords, Trophy, AlertCircle } from 'lucide-react'
import { saveAnalysis } from '@/lib/storage'

interface Report {
  report_id: string
  status: string
  riot_report: any
  cv_report:   any
  coaching:    any
  error:       string | null
}

// Poll interval in ms
const POLL_MS = 3000

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

    const poll = async () => {
      try {
        const res = await fetch(`/api/analysis/${id}`)
        if (!res.ok) throw new Error(`${res.status}`)
        const json = await res.json()
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
        if (!cancelled) setError('Could not load report — is the API running?')
      }
    }

    poll()
    return () => { cancelled = true }
  }, [id])

  // --- Loading ---
  if (!report || (report.status !== 'done' && report.status !== 'error')) {
    return (
      <div className="min-h-screen bg-[#0A0B0F] flex flex-col items-center justify-center gap-6">
        <div className="w-10 h-10 border-2 border-[#1F2130] border-t-[#FF4655] rounded-full animate-spin" />
        <p className="text-[#7A8496] text-sm">{loadingMsg}</p>
        {error && <p className="text-[#FF4655] text-xs">{error}</p>}
      </div>
    )
  }

  // --- Error ---
  if (report.status === 'error') {
    return (
      <div className="min-h-screen bg-[#0A0B0F] flex items-center justify-center px-4">
        <div className="max-w-md text-center">
          <AlertCircle className="w-10 h-10 text-[#FF4655] mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">Analysis failed</h2>
          <p className="text-[#7A8496] text-sm">{report.error || 'Unknown error'}</p>
          <Link href="/analysis/new" className="inline-block mt-6 text-[#FF4655] text-sm hover:underline">
            Try again
          </Link>
        </div>
      </div>
    )
  }

  const riot     = report.riot_report
  const coaching = report.coaching

  return (
    <div className="min-h-screen bg-[#0A0B0F]">

      {/* Nav */}
      <nav className="border-b border-[#1F2130] px-6 h-14 flex items-center justify-between sticky top-0 bg-[#0A0B0F]/95 backdrop-blur z-10">
        <Link href="/" className="font-display text-lg font-bold tracking-widest text-[#FF4655] uppercase">
          AimLab<span className="text-[#F0F1F5]">VAL</span>
        </Link>
        <Link href="/analysis/new"
          className="clip-corner-sm bg-[#FF4655] text-white text-xs font-semibold px-3 py-1.5 hover:bg-[#CC3542] transition">
          New analysis
        </Link>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-12 space-y-8 fade-in">

        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <Link href="/analysis/new" className="inline-flex items-center gap-1 text-[#42495A] text-xs hover:text-[#F0F1F5] transition mb-4">
              <ArrowLeft className="w-3 h-3" /> New analysis
            </Link>
            <h1 className="font-display text-4xl font-bold tracking-tight">
              {riot?.game_name}<span className="text-[#42495A]">#{riot?.tag_line}</span>
            </h1>
            <div className="flex items-center gap-4 mt-2 text-[#7A8496] text-sm">
              <span className="text-[#FF4655] font-semibold">{riot?.current_rank || 'Unranked'}</span>
              <span>·</span>
              <span>{riot?.matches?.length || 0} matches</span>
              <span>·</span>
              <span className={riot?.rank_delta >= 0 ? 'text-green-400' : 'text-[#FF4655]'}>
                {riot?.rank_delta >= 0 ? '+' : ''}{riot?.rank_delta} MMR
              </span>
            </div>
          </div>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-[#1F2130]">
          {[
            { label: 'Headshot %', value: `${riot?.avg_headshot_pct?.toFixed(1) ?? '—'}%`, icon: Target },
            { label: 'Avg ADR',    value: riot?.avg_adr?.toFixed(0) ?? '—',                icon: Swords },
            { label: 'Win rate',   value: `${((riot?.win_rate ?? 0) * 100).toFixed(0)}%`,  icon: Trophy },
            { label: 'Top agent',  value: riot?.top_agent ?? '—',                          icon: TrendingUp },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="bg-[#111318] p-5">
              <div className="flex items-center gap-2 text-[#42495A] text-xs uppercase tracking-widest mb-2">
                <Icon className="w-3 h-3" /> {label}
              </div>
              <div className="font-display text-3xl font-bold text-[#F0F1F5]">{value}</div>
            </div>
          ))}
        </div>

        {/* AI Coaching */}
        {coaching && (
          <div className="border border-[#1F2130] bg-[#111318]">
            <div className="border-b border-[#1F2130] px-6 py-4 flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-[#FF4655] rounded-full" />
              <span className="text-xs uppercase tracking-widest text-[#42495A]">AI Coaching Report</span>
            </div>
            <div className="p-6 space-y-6">

              <p className="text-[#F0F1F5] leading-relaxed">{coaching.summary}</p>

              {coaching.top_weakness && (
                <div className="border-l-2 border-[#FF4655] pl-4">
                  <p className="text-xs uppercase tracking-widest text-[#42495A] mb-1">Top weakness</p>
                  <p className="text-[#FF4655] font-semibold">{coaching.top_weakness}</p>
                </div>
              )}

              {coaching.tips?.length > 0 && (
                <div>
                  <p className="text-xs uppercase tracking-widest text-[#42495A] mb-3">Actionable tips</p>
                  <ol className="space-y-3">
                    {coaching.tips.map((tip: string, i: number) => (
                      <li key={i} className="flex gap-3 text-sm text-[#7A8496] leading-relaxed">
                        <span className="text-[#FF4655] font-display font-bold flex-shrink-0 w-5">{i + 1}.</span>
                        {tip}
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {coaching.encouragement && (
                <p className="text-[#7A8496] text-sm italic border-t border-[#1F2130] pt-4">
                  {coaching.encouragement}
                </p>
              )}

            </div>
          </div>
        )}

        {/* CV report (Phase 2) */}
        {report.cv_report && (
          <div className="border border-[#1F2130] bg-[#111318]">
            <div className="border-b border-[#1F2130] px-6 py-4 flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-[#FF4655] rounded-full" />
              <span className="text-xs uppercase tracking-widest text-[#42495A]">Clip Analysis</span>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-[#42495A] text-xs uppercase tracking-widest mb-1">Engagements</p>
                  <p className="font-display text-2xl font-bold">{report.cv_report.total_engagements}</p>
                </div>
                <div>
                  <p className="text-[#42495A] text-xs uppercase tracking-widest mb-1">Mistakes/min</p>
                  <p className="font-display text-2xl font-bold">{report.cv_report.mistakes_per_minute}</p>
                </div>
                <div>
                  <p className="text-[#42495A] text-xs uppercase tracking-widest mb-1">Most impactful</p>
                  <p className="font-bold text-[#FF4655]">{report.cv_report.most_impactful || '—'}</p>
                </div>
              </div>

              {report.cv_report.ranked_mistakes?.length > 0 && (
                <div className="space-y-2 pt-2">
                  {report.cv_report.ranked_mistakes.map((r: any) => (
                    <div key={r.mistake} className="flex items-center gap-3 text-sm">
                      <span className="text-[#42495A] w-4 text-right text-xs">{r.rank}.</span>
                      <span className="text-[#7A8496] w-40">{r.label}</span>
                      <div className="flex-1 bg-[#1F2130] rounded-full h-1.5">
                        <div
                          className={`h-1.5 rounded-full ${MISTAKE_COLORS[r.mistake] ?? 'bg-[#FF4655]'}`}
                          style={{ width: r.share_of_total }}
                        />
                      </div>
                      <span className="text-[#42495A] text-xs w-12 text-right">{r.share_of_total}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Match history */}
        {riot?.matches?.length > 0 && (
          <div className="border border-[#1F2130] bg-[#111318]">
            <div className="border-b border-[#1F2130] px-6 py-4 flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-[#FF4655] rounded-full" />
              <span className="text-xs uppercase tracking-widest text-[#42495A]">Recent matches</span>
            </div>
            <div className="divide-y divide-[#1F2130]">
              {riot.matches.slice(0, 8).map((m: any, i: number) => (
                <div key={i} className="flex items-center gap-4 px-6 py-3 text-sm hover:bg-[#181A22] transition">
                  <span className={`text-xs font-bold w-4 ${m.won ? 'text-green-400' : 'text-[#FF4655]'}`}>
                    {m.won ? 'W' : 'L'}
                  </span>
                  <span className="text-[#7A8496] w-24 truncate">{m.agent}</span>
                  <span className="font-mono text-[#F0F1F5]">{m.kills}/{m.deaths}/{m.assists}</span>
                  <span className="text-[#42495A] ml-auto">{m.headshot_pct?.toFixed(0)}% HS</span>
                  <span className="text-[#42495A] w-16 text-right">{m.adr?.toFixed(0)} ADR</span>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
