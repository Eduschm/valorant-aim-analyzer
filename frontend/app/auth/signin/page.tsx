'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Zap } from 'lucide-react'

export default function SignInPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const [devLoading, setDevLoading] = useState(false)
  const [error, setError] = useState('')

  const handleMagicLink = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await fetch('/api/auth/signin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })
      if (!res.ok) throw new Error('Failed to send link')
      setSent(true)
    } catch {
      setError('Failed to send magic link. Try the dev bypass below.')
    } finally {
      setLoading(false)
    }
  }

  const handleDevBypass = async () => {
    setDevLoading(true)
    setError('')
    try {
      const res = await fetch('http://localhost:8000/api/v1/dev/create-account', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'dev@localhost', riot_id: null }),
        credentials: 'include',
      })
      if (!res.ok) throw new Error('Dev bypass failed — is the API running with DEV_MODE=true?')
      router.push('/analysis/new')
    } catch (e: any) {
      setError(e.message)
    } finally {
      setDevLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-val-bg flex items-center justify-center px-4">
      <div className="w-full max-w-sm">

        <Link href="/" className="inline-flex items-center gap-2 text-val-muted text-sm hover:text-val-text transition mb-10">
          <ArrowLeft className="w-4 h-4" /> Back
        </Link>

        <div className="mb-8">
          <span className="font-display text-2xl font-bold tracking-widest text-val-red uppercase">
            AimLab<span className="text-val-text">VAL</span>
          </span>
          <h1 className="text-2xl font-bold mt-4">Sign in</h1>
          <p className="text-val-subtle text-sm mt-1">We'll send a link to your email — no password needed.</p>
        </div>

        {error && (
          <div className="border border-val-red/40 bg-val-red/5 text-val-red text-sm px-4 py-3 mb-6">
            {error}
          </div>
        )}

        {sent ? (
          <div className="border border-val-blue/40 bg-val-blue/5 text-val-blue text-sm px-4 py-4">
            <p className="font-semibold">Check your email</p>
            <p className="text-val-subtle mt-1">Link sent to {email}</p>
          </div>
        ) : (
          <form onSubmit={handleMagicLink} className="space-y-4">
            <div>
              <label className="block text-val-subtle text-xs uppercase tracking-widest mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                className="w-full bg-val-surface border border-val-border text-val-text px-4 py-3 text-sm focus:outline-none focus:border-val-red transition placeholder-val-muted"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="clip-corner w-full bg-val-red text-white font-semibold py-3 text-sm hover:bg-val-red-dark transition disabled:opacity-40">
              {loading ? 'Sending...' : 'Send magic link'}
            </button>
          </form>
        )}

        {/* Dev bypass */}
        <div className="mt-8 border-t border-val-border pt-6">
          <p className="text-val-muted text-xs uppercase tracking-widest mb-3 flex items-center gap-2">
            <Zap className="w-3 h-3 text-val-red" /> Dev bypass
          </p>
          <button
            onClick={handleDevBypass}
            disabled={devLoading}
            className="w-full border border-val-border bg-val-surface text-val-subtle text-sm py-2.5 hover:border-val-red/50 hover:text-val-text transition disabled:opacity-40">
            {devLoading ? 'Creating session...' : 'Skip auth → go straight to analysis'}
          </button>
          <p className="text-val-muted text-xs mt-2">
            Requires API running at localhost:8000 with DEV_MODE=true
          </p>
        </div>

      </div>
    </div>
  )
}
