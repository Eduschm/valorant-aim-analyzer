import { NextResponse } from 'next/server'
import { MOCK_REPORT } from '@/lib/mock/analysis'

const API_URL   = process.env.API_URL   || 'http://localhost:8000'
const MOCK_MODE = process.env.NEXT_PUBLIC_MOCK_MODE === 'true'

export async function GET(
  _request: Request,
  { params }: { params: { id: string } }
) {
  const { id } = params

  if (MOCK_MODE || id === 'mock-001') {
    return NextResponse.json({ success: true, data: MOCK_REPORT })
  }

  const res = await fetch(`${API_URL}/api/v1/report/${id}`)

  if (!res.ok) {
    const err = await res.text()
    return NextResponse.json({ success: false, error: err }, { status: res.status })
  }

  const data = await res.json()
  return NextResponse.json({ success: true, data })
}
