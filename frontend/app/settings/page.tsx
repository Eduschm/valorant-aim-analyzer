'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { clearAnalyses } from '@/lib/storage'
import { PageTransition } from '@/components/ui/PageTransition'
import { Reveal } from '@/components/ui/motion'

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
    <PageTransition className="mx-auto max-w-xl space-y-6 p-6 sm:p-8">

      <div>
        <p className="mb-2 text-xs uppercase tracking-[0.3em] text-val-accent">Settings</p>
        <h1 className="font-display text-3xl font-bold tracking-tight">Account</h1>
      </div>

      {/* Account */}
      <Reveal className="glass space-y-4 rounded-xl p-6">
        <p className="text-xs uppercase tracking-widest text-[#42495A]">Account info</p>
        <div>
          <label className="block text-[#42495A] text-xs uppercase tracking-widest mb-2">Email</label>
          <input value="dev@localhost" disabled
            className="w-full bg-[#0A0E20] border border-[#1F2130] text-[#42495A] text-sm px-4 py-2.5 disabled:opacity-50" />
          <p className="text-[#42495A] text-xs mt-1">Auth not yet enabled — email is fixed.</p>
        </div>
        <div>
          <label className="block text-[#42495A] text-xs uppercase tracking-widest mb-2">Link Riot ID</label>
          <div className="flex gap-2">
            <input
              value={riotId}
              onChange={e => setRiotId(e.target.value)}
              placeholder="PlayerName#NA1"
              className="flex-1 bg-[#0A0E20] border border-[#1F2130] text-[#F0F1F5] text-sm px-4 py-2.5 focus:outline-none focus:border-val-accent transition placeholder-[#42495A] font-mono"
            />
            <button onClick={handleLinkRiotId} disabled={savingRiot}
              className="clip-corner-sm bg-val-accent text-white text-xs font-semibold px-4 py-2 hover:bg-val-accent-dark transition disabled:opacity-40">
              {savingRiot ? '...' : 'Link'}
            </button>
          </div>
          {riotMsg && <p className="text-[#7A8496] text-xs mt-1">{riotMsg}</p>}
        </div>
      </Reveal>

      {/* Usage */}
      <Reveal className="glass space-y-3 rounded-xl p-6" delay={0.05}>
        <div className="flex items-center justify-between">
          <p className="text-xs uppercase tracking-widest text-[#42495A]">Plan</p>
          <span className="text-xs border border-[#1F2130] text-[#7A8496] px-2 py-0.5">Free tier</span>
        </div>
        <p className="text-[#7A8496] text-sm">10 analyses / month · 3 min clip cap</p>
        <button disabled
          className="clip-corner-sm text-xs border border-[#1F2130] text-[#42495A] px-4 py-2 opacity-50 cursor-not-allowed">
          Upgrade, coming soon
        </button>
      </Reveal>

      {/* Dev bypass */}
      <Reveal className="glass space-y-3 rounded-xl p-6" delay={0.1}>
        <p className="text-xs uppercase tracking-widest text-[#42495A]">Developer</p>
        <button onClick={handleDevBypass} disabled={devLoading}
          className="w-full text-left border border-[#1F2130] text-[#7A8496] text-sm py-2.5 px-4 hover:border-val-accent/40 hover:text-[#F0F1F5] transition disabled:opacity-40">
          {devLoading ? 'Creating session...' : 'Create dev session (skip auth)'}
        </button>
        {devMsg && <p className="text-[#7A8496] text-xs">{devMsg}</p>}
        <p className="text-[#42495A] text-xs">Requires API running at localhost:8000 with DEV_MODE=true</p>
      </Reveal>

      {/* Sign out */}
      <Reveal className="glass rounded-xl p-6" delay={0.15}>
        <button onClick={handleSignOut}
          className="text-val-danger text-sm hover:underline">
          Sign out and clear local data
        </button>
      </Reveal>

    </PageTransition>
  )
}
