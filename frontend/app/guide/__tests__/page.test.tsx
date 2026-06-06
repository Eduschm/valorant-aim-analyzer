import { describe, it, expect, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'

vi.mock('next/navigation', () => ({ usePathname: () => '/guide' }))

describe('GuidePage', () => {
  afterEach(cleanup)

  it('renders the guide heading and stat explanations', async () => {
    const { default: GuidePage } = await import('@/app/guide/page')
    render(<GuidePage />)
    expect(screen.getByRole('heading', { name: 'How it works', level: 1 })).toBeInTheDocument()
    expect(screen.getByText('Headshot %')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /What each stat means/i })).toBeInTheDocument()
  })
})
