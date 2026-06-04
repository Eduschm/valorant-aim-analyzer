'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { AlertCircle, ArrowRight, Target } from 'lucide-react'

export function AnalysisForm() {
  const router = useRouter()
  const [riotId, setRiotId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!riotId.includes('#')) {
      setError('Enter a valid Riot ID — format: Name#TAG')
      return
    }

    setLoading(true)
    try {
      const res = await fetch('/api/analysis/tracker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ riotId }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.error || `Server error ${res.status}`)
      }

      const { data } = await res.json()
      router.push(`/analysis/${data.id}`)
    } catch (e: any) {
      setError(e.message || 'Analysis failed. Check the API is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">

      {error && (
        <div className="flex items-start gap-3 border border-val-red/30 bg-val-red/5 px-4 py-3 text-val-red text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      <div>
        <label className="block text-val-subtle text-xs uppercase tracking-widest mb-3">
          Riot ID
        </label>
        <input
          type="text"
          value={riotId}
          onChange={e => setRiotId(e.target.value)}
          placeholder="PlayerName#NA1"
          autoFocus
          className="w-full bg-val-surface border border-val-border text-val-text text-lg px-4 py-4 focus:outline-none focus:border-val-red transition placeholder-val-muted font-mono"
        />
        <p className="text-val-muted text-xs mt-2">
          We'll pull your last 20 ranked matches via the Riot API.
        </p>
      </div>

      {/* What we check */}
      <div className="border border-val-border bg-val-surface p-4">
        <p className="text-val-subtle text-xs uppercase tracking-widest mb-3">Analyzed</p>
        <div className="grid grid-cols-2 gap-2 text-val-subtle text-sm">
          {['Headshot %', 'ADR', 'Win rate', 'Top agent', 'Top weapon', 'Rank delta'].map(item => (
            <div key={item} className="flex items-center gap-2">
              <div className="w-1 h-1 bg-val-red rounded-full flex-shrink-0" />
              {item}
            </div>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !riotId}
        className="clip-corner w-full flex items-center justify-center gap-2 bg-val-red text-white font-semibold py-4 text-sm hover:bg-val-red-dark transition disabled:opacity-40 shadow-red-glow-sm"
      >
        {loading ? (
          <>
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Analyzing...
          </>
        ) : (
          <>
            <Target className="w-4 h-4" />
            Analyze aim
            <ArrowRight className="w-4 h-4" />
          </>
        )}
      </button>

    </form>
  )
}
