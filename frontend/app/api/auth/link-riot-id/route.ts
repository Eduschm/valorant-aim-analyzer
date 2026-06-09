import { NextResponse } from 'next/server'

import { cookies } from 'next/headers'

const API_URL = process.env.API_URL || 'http://localhost:8000'

export async function POST(request: Request) {
  const { gameName, tagLine } = await request.json()
  const riot_id = `${gameName}#${tagLine}`
  let isDemo = false
  try {
    isDemo = cookies().get('demo_mode')?.value === 'true'
  } catch {}
  const isMockMode = process.env.NEXT_PUBLIC_MOCK_MODE === 'true' || isDemo

  if (isMockMode) {
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
