'use client'

import { useState } from 'react'
import { ChevronUp, ChevronDown } from 'lucide-react'

type Match = {
  match_id: string
  agent:    string
  weapon:   string
  kills:    number
  deaths:   number
  assists:  number
  headshot_pct: number
  adr:      number
  won:      boolean
}

type SortKey = 'kills' | 'deaths' | 'headshot_pct' | 'adr'

export function MatchTable({ matches }: { matches: Match[] }) {
  const [sortKey, setSortKey]   = useState<SortKey>('adr')
  const [sortAsc, setSortAsc]   = useState(false)

  const toggle = (key: SortKey) => {
    if (key === sortKey) setSortAsc(a => !a)
    else { setSortKey(key); setSortAsc(false) }
  }

  const sorted = [...matches].sort((a, b) => {
    const delta = a[sortKey] - b[sortKey]
    return sortAsc ? delta : -delta
  })

  const SortIcon = ({ k }: { k: SortKey }) =>
    sortKey === k
      ? sortAsc ? <ChevronUp className="w-3 h-3 inline" /> : <ChevronDown className="w-3 h-3 inline" />
      : <span className="w-3 h-3 inline-block" />

  const cols: { label: string; key?: SortKey; render: (m: Match) => React.ReactNode }[] = [
    { label: '',        render: m => <span className={`font-bold text-xs ${m.won ? 'text-val-green' : 'text-val-red'}`}>{m.won ? 'W' : 'L'}</span> },
    { label: 'Agent',   render: m => <span className="text-val-subtle font-mono text-xs truncate max-w-20">{m.agent.slice(0, 8)}</span> },
    { label: 'K/D/A',   render: m => <span className="font-mono">{m.kills}/{m.deaths}/{m.assists}</span> },
    { label: 'HS%',     key: 'headshot_pct', render: m => `${m.headshot_pct.toFixed(0)}%` },
    { label: 'ADR',     key: 'adr',          render: m => m.adr.toFixed(0) },
    { label: 'Weapon',  render: m => <span className="text-val-subtle text-xs truncate max-w-20">{m.weapon.slice(0, 10)}</span> },
  ]

  return (
    <div className="border border-val-border bg-val-surface overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-val-border">
            {cols.map(({ label, key }) => (
              <th key={label}
                onClick={() => key && toggle(key)}
                className={`px-4 py-3 text-left text-xs uppercase tracking-widest font-medium text-val-muted
                  ${key ? 'cursor-pointer hover:text-val-subtle select-none' : ''}`}>
                {label} {key && <SortIcon k={key} />}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((m, i) => (
            <tr key={i} className="border-b border-val-border last:border-0 hover:bg-val-surface-2 transition">
              {cols.map(({ label, render }) => (
                <td key={label} className="px-4 py-2.5 text-val-text">{render(m)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
