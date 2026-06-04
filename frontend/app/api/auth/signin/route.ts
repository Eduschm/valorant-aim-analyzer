import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const { email } = await request.json()

  // TODO: Call backend to send magic link
  // const response = await fetch(`${process.env.API_URL}/api/auth/signin`, {
  //   method: 'POST',
  //   body: JSON.stringify({ email }),
  // })

  return NextResponse.json({
    success: true,
    message: 'Magic link sent to email',
  })
}
