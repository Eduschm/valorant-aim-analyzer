import { NextResponse } from 'next/server'
import { mockAnalysis } from '@/lib/mock/analysis'

export async function GET(
  _request: Request,
  _params: { params: { id: string } }
) {
  // TODO: Use _params.params.id to fetch specific analysis
  // const { id } = _params.params
  // const response = await fetch(`${process.env.API_URL}/api/analysis/${id}`)

  // Mock response
  return NextResponse.json({
    success: true,
    data: mockAnalysis,
  })
}
