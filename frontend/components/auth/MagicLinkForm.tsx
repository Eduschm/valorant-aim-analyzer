'use client'

import { useState } from 'react'

export function MagicLinkForm() {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      setIsSubmitted(true)
      // In a real app: await fetch('/api/auth/signin', { method: 'POST', body: JSON.stringify({ email }) })
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isSubmitted) {
    return (
      <div className="bg-accent-400/10 border border-accent-400/30 rounded-lg p-6 text-center">
        <h3 className="text-lg font-semibold mb-2 text-accent-400">Check your email</h3>
        <p className="text-secondary-300">We've sent a magic link to {email}</p>
        <p className="text-secondary-400 text-sm mt-4">Click the link to verify your account and get started.</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-surface-500 border border-secondary-700 p-6 rounded-lg">
      <div>
        <label className="block text-secondary-300 text-sm font-medium mb-2">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          required
          className="w-full bg-secondary-700 border border-secondary-600 rounded-lg px-4 py-2 text-secondary-100 placeholder-secondary-400 focus:outline-none focus:border-primary-400"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-primary-400 text-secondary-900 py-2 rounded-lg font-semibold hover:bg-primary-500 transition disabled:opacity-50"
      >
        {isLoading ? 'Sending...' : 'Send Magic Link'}
      </button>
    </form>
  )
}
