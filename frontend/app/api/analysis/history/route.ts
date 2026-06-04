import { NextResponse } from 'next/server'
import { mockAnalysisHistory } from '@/lib/mock/analysis'

export async function GET() {
  // TODO: Call backend to get analysis history
  // const response = await fetch(`${process.env.API_URL}/api/analysis/history`)

  // Mock response
  return NextResponse.json({
    success: true,
    data: mockAnalysisHistory,
  })
}
