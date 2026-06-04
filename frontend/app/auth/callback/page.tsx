'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function AuthCallbackPage() {
  const router = useRouter()

  useEffect(() => {
    // In a real app, this would verify the magic link token
    // For now, just redirect to link-riot-id
    const timer = setTimeout(() => {
      router.push('/auth/link-riot-id')
    }, 1000)

    return () => clearTimeout(timer)
  }, [router])

  return (
    <div className="min-h-screen bg-secondary-900 flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-400 mb-4"></div>
        <p className="text-secondary-300">Signing you in...</p>
      </div>
    </div>
  )
}
