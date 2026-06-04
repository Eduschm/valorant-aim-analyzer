import { NextResponse } from 'next/server'

const API_URL   = process.env.API_URL   || 'http://localhost:8000'
const MOCK_MODE = process.env.NEXT_PUBLIC_MOCK_MODE === 'true'

export async function POST(request: Request) {
  const { email } = await request.json()

  if (MOCK_MODE) {
    return NextResponse.json({ success: true, message: 'Magic link sent (mock mode)' })
  }

  const res = await fetch(`${API_URL}/api/v1/auth/magic-link`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  })

  const data = await res.json()
  return NextResponse.json(data, { status: res.status })
}
