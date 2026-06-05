'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowLeft, Zap, Mail, Crosshair, CheckCircle2 } from 'lucide-react'
import { easeOut } from '@/components/ui/motion'

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
      if (!res.ok) throw new Error('Dev bypass failed. Is the API running with DEV_MODE=true?')
      router.push('/analysis/new')
    } catch (e: any) {
      setError(e.message)
    } finally {
      setDevLoading(false)
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#07080C] px-4">
      <div className="pointer-events-none absolute inset-0 bg-radial-glow" />
      <div className="pointer-events-none absolute inset-0 bg-grid aurora" />

      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: easeOut }}
        className="relative w-full max-w-sm"
      >
        <Link
          href="/"
          className="mb-8 inline-flex items-center gap-2 text-sm text-[#42495A] transition hover:text-[#F0F1F5]"
        >
          <ArrowLeft className="h-4 w-4" /> Back
        </Link>

        <div className="glass rounded-2xl p-8">
          <div className="mb-7">
            <span className="flex h-10 w-10 items-center justify-center clip-corner-sm bg-gradient-to-br from-[#FF4655] to-[#B8323D] shadow-red-glow-sm">
              <Crosshair className="h-5 w-5 text-white" />
            </span>
            <h1 className="mt-5 text-2xl font-bold">Sign in</h1>
            <p className="mt-1 text-sm text-[#7A8496]">
              We will send a link to your email. No password needed.
            </p>
          </div>

          {error && (
            <div className="mb-6 border border-[#FF4655]/40 bg-[#FF4655]/5 px-4 py-3 text-sm text-[#FF4655]">
              {error}
            </div>
          )}

          {sent ? (
            <div className="flex items-start gap-3 rounded-lg border border-emerald-500/40 bg-emerald-500/5 px-4 py-4 text-sm">
              <CheckCircle2 className="mt-0.5 h-5 w-5 flex-shrink-0 text-emerald-400" />
              <div>
                <p className="font-semibold text-emerald-300">Check your email</p>
                <p className="mt-1 text-[#7A8496]">Link sent to {email}</p>
              </div>
            </div>
          ) : (
            <form onSubmit={handleMagicLink} className="space-y-4">
              <div>
                <label className="mb-2 block text-xs uppercase tracking-widest text-[#7A8496]">
                  Email
                </label>
                <div className="relative">
                  <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#42495A]" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    required
                    className="w-full rounded-lg border border-[#1F2130] bg-[#0A0B0F] py-3 pl-10 pr-4 text-sm text-[#F0F1F5] placeholder-[#42495A] transition focus:border-[#FF4655] focus:outline-none"
                  />
                </div>
              </div>
              <motion.button
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={loading}
                className="clip-corner w-full bg-[#FF4655] py-3 text-sm font-semibold text-white transition hover:bg-[#CC3542] disabled:opacity-40"
              >
                {loading ? 'Sending...' : 'Send magic link'}
              </motion.button>
            </form>
          )}

          <div className="mt-8 border-t border-[#1F2130] pt-6">
            <p className="mb-3 flex items-center gap-2 text-xs uppercase tracking-widest text-[#42495A]">
              <Zap className="h-3 w-3 text-[#FF4655]" /> Dev bypass
            </p>
            <button
              onClick={handleDevBypass}
              disabled={devLoading}
              className="w-full rounded-lg border border-[#1F2130] bg-[#0A0B0F] py-2.5 text-sm text-[#7A8496] transition hover:border-[#FF4655]/50 hover:text-[#F0F1F5] disabled:opacity-40"
            >
              {devLoading ? 'Creating session...' : 'Skip auth, go straight to analysis'}
            </button>
            <p className="mt-2 text-xs text-[#42495A]">
              Requires API running at localhost:8000 with DEV_MODE=true
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
