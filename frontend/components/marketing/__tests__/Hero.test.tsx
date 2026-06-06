import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

describe('Hero', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({ ok: true, json: async () => [] } as Response)))
  })
  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('renders the Riot ID form directly in the hero', async () => {
    const { Hero } = await import('@/components/marketing/Hero')
    render(<Hero />)
    // The form input is present on the landing hero (no pre-click gate).
    expect(screen.getByPlaceholderText('PlayerName#NA1')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Analyze aim/i })).toBeInTheDocument()
  })

  it('marks the section with the #analyze scroll target', async () => {
    const { Hero } = await import('@/components/marketing/Hero')
    const { container } = render(<Hero />)
    expect(container.querySelector('#analyze')).not.toBeNull()
  })
})
