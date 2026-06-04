'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { AlertCircle } from 'lucide-react'

export function AnalysisForm() {
  const router = useRouter()
  const [riotId, setRiotId] = useState('Edu#1234')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      if (!riotId.includes('#')) {
        setError('Please enter a valid Riot ID (e.g. PlayerName#1234)')
        return
      }

      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // In a real app:
      // const response = await fetch('/api/analysis/tracker', {
      //   method: 'POST',
      //   body: JSON.stringify({ riotId })
      // })
      // const data = await response.json()

      router.push('/analysis/analysis_123')
    } catch (err) {
      setError('Failed to start analysis. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-surface-500 border border-secondary-700 p-8 rounded-lg">
      {error && (
        <div className="bg-primary-400/10 border border-primary-400/30 rounded-lg p-4 flex gap-3 text-primary-400">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      <div>
        <label className="block text-secondary-300 text-sm font-medium mb-2">Riot ID</label>
        <input
          type="text"
          value={riotId}
          onChange={(e) => setRiotId(e.target.value)}
          placeholder="PlayerName#1234"
          className="w-full bg-secondary-700 border border-secondary-600 rounded-lg px-4 py-3 text-secondary-100 placeholder-secondary-400 focus:outline-none focus:border-primary-400 text-lg"
        />
        <p className="text-secondary-400 text-sm mt-2">
          Enter the Valorant player ID to analyze their last 20 matches
        </p>
      </div>

      <div className="bg-secondary-600/50 border border-secondary-600 rounded-lg p-4">
        <h3 className="font-semibold mb-2 text-secondary-100">What we analyze:</h3>
        <ul className="space-y-1 text-sm text-secondary-300">
          <li>✓ Headshot percentage</li>
          <li>✓ Average damage per round (ADR)</li>
          <li>✓ Weapon efficiency</li>
          <li>✓ Agent performance</li>
          <li>✓ Rank progression</li>
        </ul>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-primary-400 text-secondary-900 py-3 rounded-lg font-semibold hover:bg-primary-500 transition disabled:opacity-50 text-lg"
      >
        {isLoading ? 'Analyzing...' : 'Start Analysis'}
      </button>
    </form>
  )
}
