import { NextResponse } from 'next/server'
import { MOCK_REPORT } from '@/lib/mock/analysis'

const API_URL   = process.env.API_URL   || 'http://localhost:8000'
const MOCK_MODE = process.env.NEXT_PUBLIC_MOCK_MODE === 'true'

export async function GET(
  _request: Request,
  { params }: { params: { id: string } }
) {
  const { id } = params

  if (MOCK_MODE) {
    return NextResponse.json({ success: true, data: { ...MOCK_REPORT, report_id: id } })
  }

  try {
    const res = await fetch(`${API_URL}/api/v1/report/${id}`)

    if (!res.ok) {
      const err = await res.text()
      return NextResponse.json(
        { success: false, error: `API error ${res.status}: ${err}` },
        { status: res.status }
      )
    }

    const data = await res.json()
    return NextResponse.json({ success: true, data })

  } catch (e: any) {
    const isConnRefused = e.message?.includes('ECONNREFUSED') || e.cause?.code === 'ECONNREFUSED'
    const msg = isConnRefused
      ? 'Backend not running — start it with: cd services/api && uvicorn main:app --reload --port 8000'
      : e.message || 'Unexpected error'

    return NextResponse.json({ success: false, error: msg }, { status: 502 })
  }
}
