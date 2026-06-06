import { describe, it, expect, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'

vi.mock('next/navigation', () => ({
  usePathname: () => '/',
}))

describe('SiteHeader', () => {
  afterEach(cleanup)

  it('renders the brand logo and all marketing nav links', async () => {
    const { SiteHeader } = await import('@/components/layout/SiteHeader')
    render(<SiteHeader />)

    expect(screen.getAllByText('AimLab').length).toBeGreaterThan(0)
    for (const label of ['Guide', 'Roadmap', 'Pricing', 'FAQ']) {
      expect(screen.getByRole('link', { name: label })).toBeInTheDocument()
    }
  })

  it('exposes a Get started link pointing at the hero form', async () => {
    const { SiteHeader } = await import('@/components/layout/SiteHeader')
    render(<SiteHeader />)
    const cta = screen.getByRole('link', { name: /Get started/i })
    expect(cta).toHaveAttribute('href', '/#analyze')
  })
})
