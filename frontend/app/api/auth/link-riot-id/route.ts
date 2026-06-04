import { NextResponse } from 'next/server'

export async function POST(_request: Request) {
  // TODO: Call backend to link Riot ID
  // const { gameName, tagLine } = await _request.json()
  // const response = await fetch(`${process.env.API_URL}/api/auth/link-riot-id`, {
  //   method: 'POST',
  //   body: JSON.stringify({ gameName, tagLine }),
  // })

  // Mock response
  await new Promise(resolve => setTimeout(resolve, 1000))

  return NextResponse.json({
    success: true,
    message: 'Riot ID linked successfully',
  })
}
