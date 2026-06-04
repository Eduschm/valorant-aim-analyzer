import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock environment variables before importing the module
vi.stubEnv('NEXT_PUBLIC_API_URL', 'http://localhost:8000')
vi.stubEnv('NEXT_PUBLIC_MOCK_MODE', 'false')

// We import after stubbing env
const { analysisApi, authApi } = await import('../api')

const mockFetch = (status: number, data: any) =>
  vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
  })

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('analysisApi.submit', () => {
  it('calls POST /api/v1/analyze with riot_id', async () => {
    global.fetch = mockFetch(200, { report_id: 'abc', status: 'queued' })
    const result = await analysisApi.submit('TenZ#NA1')
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/analyze',
      expect.objectContaining({ method: 'POST' })
    )
    expect(result.report_id).toBe('abc')
  })

  it('throws on non-2xx response', async () => {
    global.fetch = mockFetch(500, { detail: 'error' })
    await expect(analysisApi.submit('Bad#ID')).rejects.toThrow()
  })
})

describe('analysisApi.getReport', () => {
  it('calls GET /api/v1/report/{id}', async () => {
    global.fetch = mockFetch(200, { report_id: 'abc', status: 'done', riot_report: null, cv_report: null, coaching: null, error: null })
    const result = await analysisApi.getReport('abc')
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/report/abc',
      expect.any(Object)
    )
    expect(result.status).toBe('done')
  })
})

describe('authApi.requestMagicLink', () => {
  it('calls POST /api/v1/auth/magic-link', async () => {
    global.fetch = mockFetch(200, { message: 'ok' })
    await authApi.requestMagicLink('user@test.com')
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/auth/magic-link',
      expect.objectContaining({ method: 'POST' })
    )
  })
})

describe('mock mode', () => {
  it('submit returns mock-001 without fetch when MOCK_MODE=true', async () => {
    vi.stubEnv('NEXT_PUBLIC_MOCK_MODE', 'true')
    vi.resetModules()
    const { analysisApi: mockApi } = await import('../api')
    // Stub fetch AFTER module reset so it's fresh
    const fetchStub = vi.fn()
    vi.stubGlobal('fetch', fetchStub)
    const result = await mockApi.submit('Demo#NA1')
    expect(result.report_id).toBe('mock-001')
    expect(fetchStub).not.toHaveBeenCalled()
    vi.unstubAllGlobals()
  })
})
