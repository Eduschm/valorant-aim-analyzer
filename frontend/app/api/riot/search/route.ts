import { NextResponse } from 'next/server'

const RIOT_API_KEY = process.env.RIOT_API_KEY || ''
const CACHE: Record<string, { data: any[]; ts: number }> = {}
const CACHE_TTL = 60_000  // 60s

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const q = searchParams.get('q')?.trim() || ''

  if (!q || q.length < 2) return NextResponse.json([])

  // No API key → return empty (no dropdown shown, graceful fallback)
  if (!RIOT_API_KEY) return NextResponse.json([])

  const cacheKey = q.toLowerCase()
  const cached   = CACHE[cacheKey]
  if (cached && Date.now() - cached.ts < CACHE_TTL) {
    return NextResponse.json(cached.data)
  }

  try {
    // Riot Account-v1: search by prefix
    // Note: official API doesn't have a search endpoint — we query exact name#tag.
    // For autocomplete we try common tag variations.
    // A real search would require a third-party index; this is a best-effort lookup.
    const [name, tag] = q.includes('#') ? q.split('#', 2) : [q, '']
    if (!name) return NextResponse.json([])

    const tags = tag ? [tag] : ['NA1', 'EUW', 'BR1', '001']
    const results: any[] = []

    await Promise.allSettled(
      tags.slice(0, 3).map(async t => {
        const url = `https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/${encodeURIComponent(name)}/${encodeURIComponent(t)}`
        const res = await fetch(url, { headers: { 'X-Riot-Token': RIOT_API_KEY }, signal: AbortSignal.timeout(3000) })
        if (res.ok) {
          const data = await res.json()
          results.push({ game_name: data.gameName, tag_line: data.tagLine })
        }
      })
    )

    CACHE[cacheKey] = { data: results, ts: Date.now() }
    return NextResponse.json(results)
  } catch {
    return NextResponse.json([])
  }
}
