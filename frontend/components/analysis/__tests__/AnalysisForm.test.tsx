import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react'

const pushMock = vi.fn()
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: pushMock }),
}))

describe('AnalysisForm', () => {
  beforeEach(() => {
    pushMock.mockReset()
    localStorage.clear()
    // Autocomplete GETs return [], POST returns a report id.
    vi.stubGlobal(
      'fetch',
      vi.fn((_url: string, opts?: RequestInit) => {
        if (opts?.method === 'POST') {
          return Promise.resolve({
            ok: true,
            json: async () => ({ success: true, data: { id: 'report-123' } }),
          } as Response)
        }
        return Promise.resolve({ ok: true, json: async () => [] } as Response)
      }),
    )
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('renders the Riot ID input', async () => {
    const { AnalysisForm } = await import('@/components/analysis/AnalysisForm')
    render(<AnalysisForm />)
    expect(screen.getByPlaceholderText('PlayerName#NA1')).toBeInTheDocument()
  })

  it('shows a format error when the Riot ID has no tag', async () => {
    const { AnalysisForm } = await import('@/components/analysis/AnalysisForm')
    render(<AnalysisForm />)
    fireEvent.change(screen.getByPlaceholderText('PlayerName#NA1'), { target: { value: 'NoTagHere' } })
    fireEvent.click(screen.getByRole('button', { name: /Analyze aim/i }))
    expect(await screen.findByText(/Format: PlayerName#TAG/i)).toBeInTheDocument()
    expect(pushMock).not.toHaveBeenCalled()
  })

  it('submits a valid Riot ID and navigates to the report', async () => {
    const { AnalysisForm } = await import('@/components/analysis/AnalysisForm')
    render(<AnalysisForm />)
    fireEvent.change(screen.getByPlaceholderText('PlayerName#NA1'), { target: { value: 'TenZ#NA1' } })
    fireEvent.click(screen.getByRole('button', { name: /Analyze aim/i }))
    await waitFor(() => expect(pushMock).toHaveBeenCalledWith('/analysis/report-123'))
  })
})
