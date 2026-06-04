import { NextResponse } from 'next/server'
import { mockAnalysis } from '@/lib/mock/analysis'

export async function POST(request: Request) {
  const { riotId } = await request.json()

  // TODO: Call backend to start tracker analysis
  // const response = await fetch(`${process.env.API_URL}/api/analysis/tracker`, {
  //   method: 'POST',
  //   body: JSON.stringify({ riotId }),
  // })

  // Mock response
  await new Promise(resolve => setTimeout(resolve, 1500))

  return NextResponse.json({
    success: true,
    data: {
      id: mockAnalysis.id,
      status: 'processing',
    },
  })
}
