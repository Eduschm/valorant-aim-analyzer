import { describe, it, expect, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'

vi.mock('next/navigation', () => ({ usePathname: () => '/roadmap' }))

describe('RoadmapPage', () => {
  afterEach(cleanup)

  it('renders the roadmap heading and phase statuses', async () => {
    const { default: RoadmapPage } = await import('@/app/roadmap/page')
    render(<RoadmapPage />)
    expect(screen.getByRole('heading', { name: /Where we are headed/i, level: 1 })).toBeInTheDocument()
    expect(screen.getByText('Stats + AI coaching (live)')).toBeInTheDocument()
    expect(screen.getAllByText('Shipped').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Planned').length).toBeGreaterThan(0)
  })
})
