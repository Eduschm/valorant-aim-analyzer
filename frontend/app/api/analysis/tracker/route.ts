import { NextResponse } from 'next/server'

const API_URL   = process.env.API_URL   || 'http://localhost:8000'
const MOCK_MODE = process.env.NEXT_PUBLIC_MOCK_MODE === 'true'

export async function POST(request: Request) {
  const { riotId } = await request.json()

  if (MOCK_MODE) {
    await new Promise(r => setTimeout(r, 800))
    return NextResponse.json({ success: true, data: { id: 'mock-001', status: 'done' } })
  }

  try {
    const res = await fetch(`${API_URL}/api/v1/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ riot_id: riotId }),
    })

    if (!res.ok) {
      const err = await res.text()
      return NextResponse.json(
        { success: false, error: `API error ${res.status}: ${err}` },
        { status: res.status }
      )
    }

    const data = await res.json()
    return NextResponse.json({ success: true, data: { id: data.report_id, status: data.status } })

  } catch (e: any) {
    const isConnRefused = e.message?.includes('ECONNREFUSED') || e.cause?.code === 'ECONNREFUSED'
    const msg = isConnRefused
      ? `Backend not running — start it with: cd services/api && uvicorn main:app --reload --port 8000`
      : e.message || 'Unexpected error'

    return NextResponse.json({ success: false, error: msg }, { status: 502 })
  }
}
