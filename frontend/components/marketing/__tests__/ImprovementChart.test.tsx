import { describe, it, expect, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import { ImprovementChart } from '@/components/marketing/ImprovementChart'

// Note: recharts' ResponsiveContainer renders empty in jsdom (no layout box),
// so we assert the surrounding heading/caption rather than chart internals.
describe('ImprovementChart', () => {
  afterEach(cleanup)

  it('renders the section heading and caption', () => {
    render(<ImprovementChart />)
    expect(screen.getByText(/Players who upgrade improve faster/i)).toBeInTheDocument()
    expect(screen.getByText(/Illustrative cohort data/i)).toBeInTheDocument()
  })
})
