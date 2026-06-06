import { describe, it, expect, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'

vi.mock('next/navigation', () => ({ usePathname: () => '/pricing' }))

describe('PricingPage', () => {
  afterEach(cleanup)

  it('renders the pricing heading, both plans, and a pricing FAQ', async () => {
    const { default: PricingPage } = await import('@/app/pricing/page')
    render(<PricingPage />)
    expect(screen.getByRole('heading', { name: /Simple, honest pricing/i, level: 1 })).toBeInTheDocument()
    expect(screen.getByText('Free')).toBeInTheDocument()
    expect(screen.getByText('Pro')).toBeInTheDocument()
    expect(screen.getByText('$9')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /Pricing questions/i })).toBeInTheDocument()
  })
})
