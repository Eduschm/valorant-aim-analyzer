'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { AlertCircle } from 'lucide-react'

export function RiotIdLinkForm() {
  const router = useRouter()
  const [gameName, setGameName] = useState('')
  const [tagLine, setTagLine] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      // Validate format
      if (!gameName || !tagLine) {
        setError('Please enter both game name and tag')
        return
      }

      // Mock API call to validate with Riot API
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // In a real app:
      // const response = await fetch('/api/auth/link-riot-id', {
      //   method: 'POST',
      //   body: JSON.stringify({ gameName, tagLine })
      // })

      router.push('/dashboard')
    } catch (err) {
      setError('Failed to link Riot ID. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-surface-500 border border-secondary-700 p-6 rounded-lg">
      {error && (
        <div className="bg-primary-400/10 border border-primary-400/30 rounded-lg p-4 flex gap-3 text-primary-400">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-secondary-300 text-sm font-medium mb-2">Game Name</label>
          <input
            type="text"
            value={gameName}
            onChange={(e) => setGameName(e.target.value)}
            placeholder="e.g. Edu"
            className="w-full bg-secondary-700 border border-secondary-600 rounded-lg px-4 py-2 text-secondary-100 placeholder-secondary-400 focus:outline-none focus:border-primary-400"
          />
        </div>
        <div>
          <label className="block text-secondary-300 text-sm font-medium mb-2">Tag</label>
          <input
            type="text"
            value={tagLine}
            onChange={(e) => setTagLine(e.target.value)}
            placeholder="e.g. 1234"
            className="w-full bg-secondary-700 border border-secondary-600 rounded-lg px-4 py-2 text-secondary-100 placeholder-secondary-400 focus:outline-none focus:border-primary-400"
          />
        </div>
      </div>

      <p className="text-secondary-400 text-sm">
        Format: GameName#Tag (e.g. Edu#1234)
      </p>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-accent-400 text-secondary-900 py-2 rounded-lg font-semibold hover:bg-accent-500 transition disabled:opacity-50"
      >
        {isLoading ? 'Linking...' : 'Link Riot ID'}
      </button>
    </form>
  )
}
