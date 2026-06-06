import { describe, it, expect, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import { Testimonials } from '@/components/marketing/Testimonials'

describe('Testimonials', () => {
  afterEach(cleanup)

  it('renders the section heading and multiple reviews', () => {
    render(<Testimonials />)
    expect(screen.getByText(/Trusted by climbers/i)).toBeInTheDocument()
    // Each review is rendered as a <figure>; expect several.
    expect(screen.getAllByRole('figure').length).toBeGreaterThanOrEqual(3)
  })

  it('shows reviewer names and ranks', () => {
    render(<Testimonials />)
    expect(screen.getByText('Sofia R.')).toBeInTheDocument()
    expect(screen.getByText('Immortal 3')).toBeInTheDocument()
  })
})
