'use client'

import { useEffect } from 'react'
import { authApi, MeResponse } from '@/lib/api'
import { useAuthStore, User } from '@/lib/store'

export function userFromMe(me: MeResponse): User {
  const [gameName = '', tagLine = ''] = (me.riot_id ?? '').split('#')
  return {
    id: me.id,
    email: me.email,
    riotId: me.riot_id,
    gameName,
    tagLine,
    isPaid: me.is_paid,
    creditsUsed: me.credits_used,
  }
}

/**
 * Hydrates useAuthStore from GET /api/v1/me on app load.
 * Renders children immediately — auth state arrives asynchronously,
 * consumers react via the store.
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const setUser = useAuthStore((s) => s.setUser)
  const setLoading = useAuthStore((s) => s.setLoading)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    authApi
      .me()
      .then((me) => {
        if (!cancelled) setUser(me ? userFromMe(me) : null)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [setUser, setLoading])

  return <>{children}</>
}
