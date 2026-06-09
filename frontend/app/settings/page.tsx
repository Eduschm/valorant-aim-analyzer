'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { clearAnalyses } from '@/lib/storage'
import { PageTransition } from '@/components/ui/PageTransition'
import { Reveal } from '@/components/ui/motion'
import { CreditCard, Check, AlertTriangle, Sparkles, X, ToggleLeft, ToggleRight } from 'lucide-react'
import confetti from 'canvas-confetti'

export default function SettingsPage() {
  const router = useRouter()
  const [riotId,     setRiotId]     = useState('')
  const [savingRiot, setSavingRiot] = useState(false)
  const [riotMsg,    setRiotMsg]    = useState('')
  const [devLoading, setDevLoading] = useState(false)
  const [devMsg,     setDevMsg]     = useState('')

  // Sandbox settings states
  const [demoMode, setDemoMode] = useState(false)
  const [isPro, setIsPro] = useState(false)
  const [showUpgradeModal, setShowUpgradeModal] = useState(false)
  const [upgrading, setUpgrading] = useState(false)

  // Hydrate local configurations
  useEffect(() => {
    setDemoMode(localStorage.getItem('aimlab_demo_mode') === 'true')
    setIsPro(localStorage.getItem('aimlab_pro_tier') === 'true')
    setRiotId(localStorage.getItem('aimlab_last_riot_id') || '')
  }, [])

  const handleSignOut = () => {
    clearAnalyses()
    localStorage.removeItem('aimlab_pro_tier')
    localStorage.removeItem('aimlab_last_riot_id')
    localStorage.removeItem('aimlab_demo_mode')
    document.cookie = 'auth_token=; Max-Age=0; path=/'
    document.cookie = 'demo_mode=; Max-Age=0; path=/'
    router.push('/')
  }

  const handleToggleDemoMode = () => {
    const nextVal = !demoMode
    setDemoMode(nextVal)
    localStorage.setItem('aimlab_demo_mode', nextVal ? 'true' : 'false')
    document.cookie = `demo_mode=${nextVal ? 'true' : 'false'}; path=/; max-age=604800`
    
    // Create immediate feedback log
    setRiotMsg(nextVal ? 'Sandbox mode activated. Reloading...' : 'Sandbox mode deactivated. Reloading...')
    setTimeout(() => {
      window.location.reload()
    }, 800)
  }

  const handleLinkRiotId = async () => {
    if (!riotId.includes('#')) { setRiotMsg('Format: Name#TAG'); return }
    setSavingRiot(true); setRiotMsg('')
    try {
      localStorage.setItem('aimlab_last_riot_id', riotId)
      
      // If we are in demo/mock mode, we link locally instantly
      if (demoMode || localStorage.getItem('aimlab_demo_mode') === 'true') {
        setRiotMsg('Riot ID updated locally.')
        setTimeout(() => window.location.reload(), 500)
        return
      }

      // Real backend endpoint
      const res = await fetch('/api/auth/link-riot-id', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gameName: riotId.split('#')[0], tagLine: riotId.split('#')[1] }),
      })
      
      if (res.ok) {
        setRiotMsg('Riot ID linked on server.')
        setTimeout(() => window.location.reload(), 500)
      } else {
        setRiotMsg('Server stub returned 501. Try enabling "Demo Sandbox" above to link locally!')
      }
    } catch {
      setRiotMsg('Failed to connect to API. Try enabling "Demo Sandbox" above to link locally!')
    } finally {
      setSavingRiot(false)
    }
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

  const handleSimulatePayment = () => {
    setUpgrading(true)
    setTimeout(() => {
      setUpgrading(false)
      setShowUpgradeModal(false)
      setIsPro(true)
      localStorage.setItem('aimlab_pro_tier', 'true')
      
      // Fire visual reward confetti
      confetti({
        particleCount: 120,
        spread: 80,
        origin: { y: 0.6 }
      })

      // Reload to propagate pro status in app shell
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    }, 1500)
  }

  const handleDowngrade = () => {
    setIsPro(false)
    localStorage.removeItem('aimlab_pro_tier')
    window.location.reload()
  }

  return (
    <PageTransition className="mx-auto max-w-xl space-y-6 p-6 sm:p-8 relative">

      <div>
        <p className="mb-2 text-xs uppercase tracking-[0.3em] text-val-accent">Settings</p>
        <h1 className="font-display text-3xl font-bold tracking-tight">Account Configuration</h1>
      </div>

      {/* Demo mode trigger card */}
      <Reveal className="glass border border-val-cyan/25 bg-val-cyan/[0.02] space-y-4 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-val-cyan uppercase tracking-wider">Demo Sandbox Mode</h3>
            <p className="text-xs text-[#7A8496] mt-1 leading-relaxed">
              Bypasses backend API keys. Uses realistic mock datasets for instant testing.
            </p>
          </div>
          <button 
            onClick={handleToggleDemoMode}
            className="text-val-cyan transition transform active:scale-95"
          >
            {demoMode ? (
              <ToggleRight className="h-10 w-10 text-val-cyan" />
            ) : (
              <ToggleLeft className="h-10 w-10 text-[#42495A]" />
            )}
          </button>
        </div>
      </Reveal>

      {/* Account Profile Card */}
      <Reveal className="glass space-y-4 rounded-xl p-6" delay={0.05}>
        <p className="text-xs uppercase tracking-widest text-[#42495A] font-bold">Profile Details</p>
        <div>
          <label className="block text-[#42495A] text-xs uppercase tracking-widest mb-2">Linked Email</label>
          <input value="dev@localhost" disabled
            className="w-full bg-[#0A0E20] border border-[#1F2130] text-[#42495A] text-sm px-4 py-2.5 disabled:opacity-50 font-mono" />
          <p className="text-[#42495A] text-[10px] mt-1">Free Sandbox verification profile.</p>
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
              className="clip-corner-sm bg-val-accent text-white text-xs font-semibold px-5 py-2 hover:bg-val-accent-dark transition disabled:opacity-40 shadow-accent-glow-sm">
              {savingRiot ? 'Saving...' : 'Link ID'}
            </button>
          </div>
          {riotMsg && (
            <p className={`text-xs mt-1.5 font-mono ${riotMsg.includes('Linked') || riotMsg.includes('updated') ? 'text-emerald-400' : 'text-val-accent'}`}>
              {riotMsg}
            </p>
          )}
        </div>
      </Reveal>

      {/* Billing Upgrade Tier card */}
      <Reveal className="glass space-y-4 rounded-xl p-6" delay={0.1}>
        <div className="flex items-center justify-between border-b border-[#1F2130] pb-3">
          <div>
            <p className="text-xs uppercase tracking-widest text-[#42495A] font-bold">Billing Plan</p>
            <p className="text-[#F0F1F5] font-display text-lg font-bold mt-1">
              {isPro ? 'Pro Subscription' : 'Free Tier Account'}
            </p>
          </div>
          <span className={`text-[10px] border px-2 py-0.5 uppercase tracking-wider font-bold ${
            isPro ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400' : 'border-[#1F2130] text-[#7A8496]'
          }`}>
            {isPro ? 'Active Pro' : 'Free Trial'}
          </span>
        </div>
        
        <p className="text-[#7A8496] text-xs leading-normal">
          {isPro 
            ? '✓ Unlimited aim analyses monthly · ✓ Unlimited CV clip uploads (up to 3 min each).' 
            : '10 analyses / month · Standard Riot metrics. Upgrade to Pro for AI coaching & clip processing.'
          }
        </p>

        {isPro ? (
          <button 
            onClick={handleDowngrade}
            className="text-xs text-val-danger hover:underline font-semibold block"
          >
            Cancel Subscription (Downgrade to Free)
          </button>
        ) : (
          <button 
            onClick={() => setShowUpgradeModal(true)}
            className="clip-corner w-full flex items-center justify-center gap-2 bg-gradient-to-r from-val-accent to-purple-600 text-white font-semibold py-3 text-xs hover:from-val-accent-dark hover:to-purple-700 transition shadow-accent-glow"
          >
            <Sparkles className="w-4 h-4" /> Upgrade to Pro ($9/mo)
          </button>
        )}
      </Reveal>

      {/* Stripe Payment Dialog Simulation Modal */}
      {showUpgradeModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="glass max-w-sm w-full rounded-2xl overflow-hidden border border-white/10 shadow-[0_0_50px_rgba(67,97,238,0.25)]"
          >
            <div className="flex items-center justify-between border-b border-[#1F2130] bg-[#0E1225] px-5 py-4">
              <div className="flex items-center gap-2">
                <CreditCard className="w-4 h-4 text-val-accent" />
                <span className="font-display font-bold text-sm text-[#F0F1F5] uppercase tracking-wider">
                  Secure Checkout
                </span>
              </div>
              <button 
                onClick={() => setShowUpgradeModal(false)}
                className="text-[#7A8496] hover:text-[#F0F1F5] transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-6 space-y-4 font-mono text-xs">
              <div className="border border-[#1F2130] bg-[#0A0D1A] p-4 rounded-lg space-y-2">
                <div className="flex justify-between text-[#7A8496]">
                  <span>AimLab VAL Pro</span>
                  <span className="text-[#F0F1F5]">$9.00 / mo</span>
                </div>
                <div className="flex justify-between font-bold border-t border-[#1F2130] pt-2 text-[#F0F1F5]">
                  <span>Due Today</span>
                  <span className="text-emerald-400">$0.00 (7-Day Trial)</span>
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-[#42495A] text-[9px] uppercase tracking-widest mb-1.5">Card Number</label>
                  <div className="relative">
                    <input 
                      type="text" 
                      value="4242 •••• •••• 4242" 
                      disabled
                      className="w-full bg-[#0E1225] border border-[#1F2130] text-[#7A8496] px-3 py-2.5 rounded disabled:opacity-80 font-mono" 
                    />
                    <CreditCard className="absolute right-3 top-3 w-4 h-4 text-[#42495A]" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[#42495A] text-[9px] uppercase tracking-widest mb-1.5">Expires</label>
                    <input type="text" value="12 / 29" disabled className="w-full bg-[#0E1225] border border-[#1F2130] text-[#7A8496] px-3 py-2.5 rounded disabled:opacity-80 text-center" />
                  </div>
                  <div>
                    <label className="block text-[#42495A] text-[9px] uppercase tracking-widest mb-1.5">CVC</label>
                    <input type="text" value="•••" disabled className="w-full bg-[#0E1225] border border-[#1F2130] text-[#7A8496] px-3 py-2.5 rounded disabled:opacity-80 text-center" />
                  </div>
                </div>
              </div>

              <button
                onClick={handleSimulatePayment}
                disabled={upgrading}
                className="w-full clip-corner-sm bg-emerald-500 hover:bg-emerald-600 text-white font-bold py-3.5 transition disabled:opacity-40 uppercase tracking-widest text-[10px]"
              >
                {upgrading ? 'Authorizing Card...' : 'Confirm Checkout'}
              </button>

              <p className="text-[9px] text-[#42495A] leading-normal text-center">
                🔒 SSL Encrypted Checkout. Simulated Stripe API payment transaction.
              </p>
            </div>
          </motion.div>
        </div>
      )}

      {/* Dev bypass (only visible if not in Demo Mode to avoid clutter) */}
      {!demoMode && (
        <Reveal className="glass space-y-3 rounded-xl p-6" delay={0.15}>
          <p className="text-xs uppercase tracking-widest text-[#42495A] font-bold">Developer Bypass</p>
          <button onClick={handleDevBypass} disabled={devLoading}
            className="w-full text-left border border-[#1F2130] text-[#7A8496] text-xs py-2.5 px-4 hover:border-val-accent/40 hover:text-[#F0F1F5] transition disabled:opacity-40 font-mono">
            {devLoading ? 'Creating session...' : 'Create dev session (skip auth)'}
          </button>
          {devMsg && <p className="text-[#7A8496] text-xs">{devMsg}</p>}
          <p className="text-[#42495A] text-[10px]">Requires API running at localhost:8000 with DEV_MODE=true</p>
        </Reveal>
      )}

      {/* Sign out */}
      <Reveal className="glass rounded-xl p-6" delay={0.2}>
        <button onClick={handleSignOut}
          className="text-val-danger text-sm hover:underline font-semibold">
          Sign out and clear local data
        </button>
      </Reveal>

    </PageTransition>
  )
}
