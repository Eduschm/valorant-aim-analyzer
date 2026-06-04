import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.stubEnv('NEXT_PUBLIC_MOCK_MODE', 'false')
vi.stubEnv('API_URL', 'http://localhost:8000')

const { POST } = await import('../analysis/tracker/route')

function mockRequest(body: object) {
  return new Request('http://localhost/api/analysis/tracker', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

beforeEach(() => vi.restoreAllMocks())

describe('POST /api/analysis/tracker', () => {

  it('forwards to backend and returns report_id', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ report_id: 'xyz', status: 'queued' }),
    } as any)

    const res = await POST(mockRequest({ riotId: 'TenZ#NA1' }))
    const data = await res.json()
    expect(data.success).toBe(true)
    expect(data.data.id).toBe('xyz')
  })

  it('returns 502 with helpful message on ECONNREFUSED', async () => {
    const err = new TypeError('fetch failed')
    ;(err as any).cause = { code: 'ECONNREFUSED' }
    global.fetch = vi.fn().mockRejectedValue(err)

    const res = await POST(mockRequest({ riotId: 'TenZ#NA1' }))
    expect(res.status).toBe(502)
    const data = await res.json()
    expect(data.error).toMatch(/Backend not running/)
  })

  it('returns backend status code on non-ok response', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      text: () => Promise.resolve('Validation error'),
    } as any)

    const res = await POST(mockRequest({ riotId: 'Bad' }))
    expect(res.status).toBe(422)
  })

})
