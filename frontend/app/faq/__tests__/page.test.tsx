import { describe, it, expect, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'

vi.mock('next/navigation', () => ({ usePathname: () => '/faq' }))

describe('FaqPage', () => {
  afterEach(cleanup)

  it('renders the FAQ heading and questions', async () => {
    const { default: FaqPage } = await import('@/app/faq/page')
    render(<FaqPage />)
    expect(screen.getByRole('heading', { name: /Frequently asked questions/i, level: 1 })).toBeInTheDocument()
    expect(screen.getByText(/Is this allowed by Riot/i)).toBeInTheDocument()
  })
})
