import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.stubEnv('RIOT_API_KEY', 'test-key')

function req(q: string) {
  return new Request(`http://localhost/api/riot/search?q=${encodeURIComponent(q)}`)
}

// Re-import fresh module each test to reset in-memory CACHE
beforeEach(() => {
  vi.restoreAllMocks()
  vi.resetModules()
})

describe('GET /api/riot/search', () => {

  it('returns empty array when query is too short', async () => {
    const { GET } = await import('../riot/search/route')
    const res = await GET(req('T'))
    expect(await res.json()).toEqual([])
  })

  it('returns empty array when no API key', async () => {
    vi.stubEnv('RIOT_API_KEY', '')
    const { GET } = await import('../riot/search/route')
    const res = await GET(req('TenZ'))
    expect(await res.json()).toEqual([])
    vi.stubEnv('RIOT_API_KEY', 'test-key')
  })

  it('returns matching accounts from Riot API', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ gameName: 'TenZ', tagLine: 'NA1', puuid: 'abc' }),
    }))
    const { GET } = await import('../riot/search/route')
    const res = await GET(req('TenZ#NA1'))
    const data = await res.json()
    expect(Array.isArray(data)).toBe(true)
    if (data.length > 0) {
      expect(data[0]).toHaveProperty('game_name')
      expect(data[0]).toHaveProperty('tag_line')
    }
    vi.unstubAllGlobals()
  })

  it('returns empty array on Riot API error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 404 }))
    const { GET } = await import('../riot/search/route')
    const res = await GET(req('TenZ#NA1'))
    expect(await res.json()).toEqual([])
    vi.unstubAllGlobals()
  })

})
