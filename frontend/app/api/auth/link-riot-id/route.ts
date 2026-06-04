import { NextResponse } from 'next/server'

const API_URL   = process.env.API_URL   || 'http://localhost:8000'
const MOCK_MODE = process.env.NEXT_PUBLIC_MOCK_MODE === 'true'

export async function POST(request: Request) {
  const { gameName, tagLine } = await request.json()
  const riot_id = `${gameName}#${tagLine}`

  if (MOCK_MODE) {
    await new Promise(r => setTimeout(r, 500))
    return NextResponse.json({ success: true, message: 'Riot ID linked (mock mode)' })
  }

  const res = await fetch(`${API_URL}/api/v1/auth/riot-id`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ riot_id }),
  })

  const data = await res.json()
  return NextResponse.json(data, { status: res.status })
}
