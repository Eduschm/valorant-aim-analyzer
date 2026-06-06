'use client'

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

/**
 * Fabricated paid-vs-free improvement data. Placeholder until real cohort
 * metrics exist. Shows average headshot % climbing faster for paying users.
 */
const DATA = [
  { week: 'W1', paid: 19.2, free: 19.0 },
  { week: 'W2', paid: 21.0, free: 19.4 },
  { week: 'W3', paid: 22.6, free: 19.9 },
  { week: 'W4', paid: 24.1, free: 20.3 },
  { week: 'W5', paid: 25.4, free: 20.6 },
  { week: 'W6', paid: 26.8, free: 21.0 },
  { week: 'W7', paid: 27.9, free: 21.3 },
  { week: 'W8', paid: 29.1, free: 21.5 },
]

export function ImprovementChart() {
  return (
    <section className="relative mx-auto max-w-6xl px-6 py-20">
      <p className="mb-2 text-xs uppercase tracking-[0.3em] text-val-accent">The data</p>
      <h2 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
        Players who upgrade improve faster
      </h2>
      <p className="mt-3 max-w-xl text-sm leading-relaxed text-[#7A8496]">
        Average headshot % over 8 weeks. Pro users run more reports, act on more fixes, and climb
        a full +10% HS while free users plateau. (Illustrative cohort data.)
      </p>

      <div className="glass mt-10 rounded-2xl p-6">
        <div className="h-[320px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={DATA} margin={{ top: 10, right: 16, left: -8, bottom: 0 }}>
              <defs>
                <linearGradient id="paidFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#4361EE" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#4361EE" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="freeFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#42495A" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#42495A" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2130" vertical={false} />
              <XAxis dataKey="week" stroke="#42495A" tick={{ fill: '#42495A', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis
                stroke="#42495A"
                tick={{ fill: '#42495A', fontSize: 12 }}
                axisLine={false}
                tickLine={false}
                width={40}
                unit="%"
              />
              <Tooltip
                contentStyle={{ background: '#0B0C12', border: '1px solid #1F2130', borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: '#7A8496' }}
                formatter={(v: number, name: string) => [`${v}%`, name === 'paid' ? 'Pro' : 'Free']}
              />
              <Legend
                formatter={(value) => (value === 'paid' ? 'Pro users' : 'Free users')}
                wrapperStyle={{ fontSize: 12, color: '#7A8496' }}
              />
              <Area type="monotone" dataKey="free" stroke="#42495A" strokeWidth={2} fill="url(#freeFill)" />
              <Area type="monotone" dataKey="paid" stroke="#4361EE" strokeWidth={2.5} fill="url(#paidFill)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  )
}
