'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { AlertCircle, ArrowRight, Target, ChevronDown } from 'lucide-react'

const REGIONS = ['NA', 'EU', 'AP', 'BR', 'LATAM', 'KR']
const EXAMPLES = ['TenZ#NA1', 'Shroud#NA1', 'ScreaM#EUW']
const STORAGE_KEY = 'aimlab_last_riot_id'

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return debounced
}

export function AnalysisForm() {
  const router = useRouter()

  const [riotId,      setRiotId]      = useState('')
  const [region,      setRegion]      = useState('NA')
  const [loading,     setLoading]     = useState(false)
  const [error,       setError]       = useState('')
  const [suggestions, setSuggestions] = useState<{ game_name: string; tag_line: string }[]>([])
  const [showDrop,    setShowDrop]    = useState(false)
  const [lastUsed,    setLastUsed]    = useState('')
  const dropRef = useRef<HTMLDivElement>(null)

  const debounced = useDebounce(riotId, 300)

  // Restore last used
  useEffect(() => {
    const v = localStorage.getItem(STORAGE_KEY) || ''
    setLastUsed(v)
  }, [])

  // Autocomplete
  useEffect(() => {
    if (debounced.length < 2) { setSuggestions([]); return }
    fetch(`/api/riot/search?q=${encodeURIComponent(debounced)}`)
      .then(r => r.json())
      .then(data => { setSuggestions(data); setShowDrop(data.length > 0) })
      .catch(() => {})
  }, [debounced])

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropRef.current && !dropRef.current.contains(e.target as Node)) setShowDrop(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!riotId.includes('#')) { setError('Format: PlayerName#TAG (e.g. TenZ#NA1)'); return }
    setLoading(true)
    try {
      const res = await fetch('/api/analysis/tracker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ riotId, region }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.error || `Server error ${res.status}`)
      }
      const { data } = await res.json()
      localStorage.setItem(STORAGE_KEY, riotId)
      router.push(`/analysis/${data.id}`)
    } catch (e: any) {
      setError(e.message || 'Analysis failed.')
    } finally {
      setLoading(false)
    }
  }

  const pickSuggestion = (s: { game_name: string; tag_line: string }) => {
    setRiotId(`${s.game_name}#${s.tag_line}`)
    setShowDrop(false)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">

      {error && (
        <div className="flex items-start gap-3 border border-val-red/30 bg-val-red/5 px-4 py-3 text-val-red text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" /> {error}
        </div>
      )}

      {/* Riot ID input + autocomplete */}
      <div>
        <label className="block text-val-muted text-xs uppercase tracking-widest mb-2">Riot ID</label>
        <div className="relative" ref={dropRef}>
          <input
            type="text"
            value={riotId}
            onChange={e => { setRiotId(e.target.value); setShowDrop(true) }}
            onFocus={() => suggestions.length > 0 && setShowDrop(true)}
            placeholder="PlayerName#NA1"
            autoFocus
            className="w-full bg-val-surface border border-val-border text-val-text text-lg px-4 py-4 focus:outline-none focus:border-val-red transition placeholder-val-muted font-mono"
          />
          {showDrop && suggestions.length > 0 && (
            <div className="absolute left-0 right-0 top-full border border-val-border bg-val-surface-2 z-10 shadow-red-glow-sm">
              {suggestions.map((s, i) => (
                <button type="button" key={i}
                  onClick={() => pickSuggestion(s)}
                  className="w-full text-left px-4 py-2.5 text-sm text-val-text hover:bg-val-surface font-mono border-b border-val-border last:border-0 transition">
                  {s.game_name}<span className="text-val-muted">#{s.tag_line}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Last used + examples */}
        <div className="flex flex-wrap gap-2 mt-2">
          {lastUsed && lastUsed !== riotId && (
            <button type="button" onClick={() => setRiotId(lastUsed)}
              className="text-xs text-val-subtle border border-val-border px-2 py-1 hover:border-val-red/50 hover:text-val-text transition font-mono">
              ↩ {lastUsed}
            </button>
          )}
          {EXAMPLES.map(ex => (
            <button type="button" key={ex} onClick={() => setRiotId(ex)}
              className="text-xs text-val-muted border border-val-border px-2 py-1 hover:border-val-border-2 transition font-mono">
              {ex}
            </button>
          ))}
        </div>
      </div>

      {/* Region */}
      <div>
        <label className="block text-val-muted text-xs uppercase tracking-widest mb-2">Region</label>
        <div className="relative inline-block">
          <select value={region} onChange={e => setRegion(e.target.value)}
            className="appearance-none bg-val-surface border border-val-border text-val-text text-sm px-4 py-2.5 pr-8 focus:outline-none focus:border-val-red transition cursor-pointer">
            {REGIONS.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
          <ChevronDown className="absolute right-2 top-3 w-4 h-4 text-val-muted pointer-events-none" />
        </div>
      </div>

      {/* What we analyze */}
      <div className="border border-val-border bg-val-surface p-4">
        <p className="text-val-muted text-xs uppercase tracking-widest mb-3">Analyzed</p>
        <div className="grid grid-cols-2 gap-1.5 text-val-subtle text-sm">
          {['Headshot %', 'ADR', 'Win rate', 'Top agent', 'Top weapon', 'Rank delta'].map(item => (
            <div key={item} className="flex items-center gap-2">
              <div className="w-1 h-1 bg-val-red rounded-full flex-shrink-0" /> {item}
            </div>
          ))}
        </div>
      </div>

      <button type="submit" disabled={loading || !riotId}
        className="clip-corner w-full flex items-center justify-center gap-2 bg-val-red text-white font-semibold py-4 text-sm hover:bg-val-red-dark transition disabled:opacity-40 shadow-red-glow-sm">
        {loading ? (
          <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Analyzing...</>
        ) : (
          <><Target className="w-4 h-4" /> Analyze aim <ArrowRight className="w-4 h-4" /></>
        )}
      </button>
    </form>
  )
}
