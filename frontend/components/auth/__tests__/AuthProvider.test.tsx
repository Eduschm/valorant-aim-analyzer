import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'

vi.stubEnv('NEXT_PUBLIC_API_URL', 'http://localhost:8000')
vi.stubEnv('NEXT_PUBLIC_MOCK_MODE', 'false')

const { AuthProvider, userFromMe } = await import('../AuthProvider')
const { useAuthStore } = await import('@/lib/store')
const { authApi } = await import('@/lib/api')

const ME = {
  id: 'user-1',
  email: 'edu@example.com',
  riot_id: 'TestPlayer#NA1',
  is_paid: false,
  credits_used: 3,
  created_at: '2026-06-09T00:00:00',
}

beforeEach(() => {
  vi.restoreAllMocks()
  useAuthStore.setState({ user: null, isAuthenticated: false, isLoading: false })
})

describe('userFromMe', () => {
  it('maps the /me payload and splits the Riot ID', () => {
    const user = userFromMe(ME)
    expect(user.gameName).toBe('TestPlayer')
    expect(user.tagLine).toBe('NA1')
    expect(user.creditsUsed).toBe(3)
    expect(user.isPaid).toBe(false)
  })

  it('handles a null riot_id', () => {
    const user = userFromMe({ ...ME, riot_id: null })
    expect(user.riotId).toBeNull()
    expect(user.gameName).toBe('')
    expect(user.tagLine).toBe('')
  })
})

describe('AuthProvider', () => {
  it('renders children immediately', () => {
    vi.spyOn(authApi, 'me').mockResolvedValue(null)
    render(
      <AuthProvider>
        <div>app content</div>
      </AuthProvider>
    )
    expect(screen.getByText('app content')).toBeDefined()
  })

  it('hydrates the auth store when /me returns a user', async () => {
    vi.spyOn(authApi, 'me').mockResolvedValue(ME)
    render(<AuthProvider>x</AuthProvider>)
    await waitFor(() => {
      expect(useAuthStore.getState().isAuthenticated).toBe(true)
    })
    expect(useAuthStore.getState().user?.email).toBe('edu@example.com')
    expect(useAuthStore.getState().isLoading).toBe(false)
  })

  it('leaves the store signed out when /me returns null', async () => {
    vi.spyOn(authApi, 'me').mockResolvedValue(null)
    render(<AuthProvider>x</AuthProvider>)
    await waitFor(() => {
      expect(useAuthStore.getState().isLoading).toBe(false)
    })
    expect(useAuthStore.getState().isAuthenticated).toBe(false)
    expect(useAuthStore.getState().user).toBeNull()
  })
})
