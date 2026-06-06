import { describe, it, expect, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'

vi.mock('next/navigation', () => ({ usePathname: () => '/pricing' }))

describe('PricingTable', () => {
  afterEach(cleanup)

  it('renders Free and Pro plans with the $9 price', async () => {
    const { PricingTable } = await import('@/components/marketing/PricingTable')
    render(<PricingTable />)
    expect(screen.getByText('Free')).toBeInTheDocument()
    expect(screen.getByText('Pro')).toBeInTheDocument()
    expect(screen.getByText('$9')).toBeInTheDocument()
  })

  it('links both plan CTAs to sign in', async () => {
    const { PricingTable } = await import('@/components/marketing/PricingTable')
    render(<PricingTable />)
    const ctas = screen.getAllByRole('link')
    expect(ctas.length).toBeGreaterThanOrEqual(2)
    for (const cta of ctas) {
      expect(cta).toHaveAttribute('href', '/auth/signin')
    }
  })
})
