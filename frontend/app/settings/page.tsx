'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { clearAnalyses } from '@/lib/storage'

const DEV_MODE  = process.env.NEXT_PUBLIC_MOCK_MODE !== 'true'   // true when using real API

export default function SettingsPage() {
  const router = useRouter()
  const [riotId,     setRiotId]     = useState('')
  const [savingRiot, setSavingRiot] = useState(false)
  const [riotMsg,    setRiotMsg]    = useState('')
  const [devLoading, setDevLoading] = useState(false)
  const [devMsg,     setDevMsg]     = useState('')

  const handleSignOut = () => {
    clearAnalyses()
    document.cookie = 'auth_token=; Max-Age=0; path=/'
    router.push('/')
  }

  const handleLinkRiotId = async () => {
    if (!riotId.includes('#')) { setRiotMsg('Format: Name#TAG'); return }
    setSavingRiot(true); setRiotMsg('')
    try {
      const res = await fetch('/api/auth/link-riot-id', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gameName: riotId.split('#')[0], tagLine: riotId.split('#')[1] }),
      })
      setRiotMsg(res.ok ? 'Riot ID linked.' : 'Failed — is the API running?')
    } catch { setRiotMsg('Failed to connect to API.') }
    finally { setSavingRiot(false) }
  }

  const handleDevBypass = async () => {
    setDevLoading(true); setDevMsg('')
    try {
      const res = await fetch('http://localhost:8000/api/v1/dev/create-account', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'dev@localhost' }),
        credentials: 'include',
      })
      setDevMsg(res.ok ? 'Dev session created.' : 'Failed — start API with DEV_MODE=true')
    } catch { setDevMsg('Cannot reach API at localhost:8000') }
    finally { setDevLoading(false) }
  }

  return (
    <div className="p-8 max-w-xl space-y-6 fade-in">

      <div>
        <p className="text-xs uppercase tracking-widest text-val-muted mb-2">Settings</p>
        <h1 className="font-display text-3xl font-bold tracking-tight">Account</h1>
      </div>

      {/* Account */}
      <div className="border border-val-border bg-val-surface p-6 space-y-4">
        <p className="text-xs uppercase tracking-widest text-val-muted">Account info</p>
        <div>
          <label className="block text-val-muted text-xs uppercase tracking-widest mb-2">Email</label>
          <input value="dev@localhost" disabled
            className="w-full bg-val-bg border border-val-border text-val-muted text-sm px-4 py-2.5 disabled:opacity-50" />
          <p className="text-val-muted text-xs mt-1">Auth not yet enabled — email is fixed.</p>
        </div>
        <div>
          <label className="block text-val-muted text-xs uppercase tracking-widest mb-2">Link Riot ID</label>
          <div className="flex gap-2">
            <input
              value={riotId}
              onChange={e => setRiotId(e.target.value)}
              placeholder="PlayerName#NA1"
              className="flex-1 bg-val-bg border border-val-border text-val-text text-sm px-4 py-2.5 focus:outline-none focus:border-val-red transition placeholder-val-muted font-mono"
            />
            <button onClick={handleLinkRiotId} disabled={savingRiot}
              className="clip-corner-sm bg-val-red text-white text-xs font-semibold px-4 py-2 hover:bg-val-red-dark transition disabled:opacity-40">
              {savingRiot ? '...' : 'Link'}
            </button>
          </div>
          {riotMsg && <p className="text-val-subtle text-xs mt-1">{riotMsg}</p>}
        </div>
      </div>

      {/* Usage */}
      <div className="border border-val-border bg-val-surface p-6 space-y-3">
        <div className="flex items-center justify-between">
          <p className="text-xs uppercase tracking-widest text-val-muted">Plan</p>
          <span className="text-xs border border-val-border text-val-subtle px-2 py-0.5">Free tier</span>
        </div>
        <p className="text-val-subtle text-sm">10 analyses / month · 3 min clip cap</p>
        <button disabled
          className="clip-corner-sm text-xs border border-val-border text-val-muted px-4 py-2 opacity-50 cursor-not-allowed">
          Upgrade — coming soon
        </button>
      </div>

      {/* Dev bypass */}
      <div className="border border-val-border bg-val-surface p-6 space-y-3">
        <p className="text-xs uppercase tracking-widest text-val-muted">Developer</p>
        <button onClick={handleDevBypass} disabled={devLoading}
          className="w-full text-left border border-val-border text-val-subtle text-sm py-2.5 px-4 hover:border-val-red/40 hover:text-val-text transition disabled:opacity-40">
          {devLoading ? 'Creating session...' : 'Create dev session (skip auth)'}
        </button>
        {devMsg && <p className="text-val-subtle text-xs">{devMsg}</p>}
        <p className="text-val-muted text-xs">Requires API running at localhost:8000 with DEV_MODE=true</p>
      </div>

      {/* Sign out */}
      <div className="border border-val-border bg-val-surface p-6">
        <button onClick={handleSignOut}
          className="text-val-red text-sm hover:underline">
          Sign out and clear local data
        </button>
      </div>

    </div>
  )
}
