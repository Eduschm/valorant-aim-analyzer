import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, cleanup } from '@testing-library/react'

vi.mock('next/navigation', () => ({
  useParams: () => ({ id: 'test-report' }),
}))

describe('AnalysisReportPage', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

  it('shows an error page when the report API is unreachable', async () => {
    const fetchMock = vi.mocked(global.fetch as typeof fetch)
    fetchMock.mockResolvedValue({
      ok: false,
      status: 502,
      text: async () => 'Backend offline',
    } as any)

    const { default: AnalysisReportPage } = await import('@/app/analysis/[id]/page')
    render(<AnalysisReportPage />)

    await waitFor(() => expect(screen.getByText('Analysis failed')).toBeInTheDocument())
    // The page surfaces the HTTP status code as the error message.
    expect(screen.getByText('502')).toBeInTheDocument()
  })

  it('renders the report after a successful poll', async () => {
    const fetchMock = vi.mocked(global.fetch as typeof fetch)
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({
        success: true,
        data: {
          report_id: 'test-report',
          status: 'done',
          riot_report: {
            game_name: 'TestPlayer',
            tag_line: 'NA1',
            current_rank: 'Gold 2',
            rank_delta: 5,
            matches: [],
            avg_headshot_pct: 25,
            avg_adr: 150,
            top_agent: 'Jett',
            win_rate: 0.6,
          },
          cv_report: null,
          coaching: {
            summary: 'Here is your coaching report.',
            top_weakness: 'Aim placement',
            tips: ['Track your crosshair better.'],
            encouragement: 'Keep going.',
            raw_response: '{}',
          },
          error: null,
        },
      }),
    } as any)

    const { default: AnalysisReportPage } = await import('@/app/analysis/[id]/page')
    render(<AnalysisReportPage />)

    // game_name and #tag_line render in separate elements, so match the heading's accessible name.
    await waitFor(() => expect(screen.getByRole('heading', { name: 'TestPlayer#NA1' })).toBeInTheDocument())
    expect(screen.getByText('Gold 2')).toBeInTheDocument()
    expect(screen.getByText('Here is your coaching report.')).toBeInTheDocument()
  })
})
