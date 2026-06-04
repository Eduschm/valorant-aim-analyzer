'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'

export function AuthGuard({
  children,
  requiredAuth = true,
}: {
  children: React.ReactNode
  requiredAuth?: boolean
}) {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuthStore()

  useEffect(() => {
    if (!isLoading) {
      if (requiredAuth && !isAuthenticated) {
        router.push('/auth/signin')
      } else if (!requiredAuth && isAuthenticated) {
        router.push('/dashboard')
      }
    }
  }, [isAuthenticated, isLoading, requiredAuth, router])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-secondary-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-400 mb-4"></div>
          <p className="text-secondary-300">Loading...</p>
        </div>
      </div>
    )
  }

  if (requiredAuth && !isAuthenticated) {
    return null
  }

  if (!requiredAuth && isAuthenticated) {
    return null
  }

  return <>{children}</>
}
