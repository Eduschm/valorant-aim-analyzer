import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Valorant Aim Analyzer',
  description: 'AI-powered aim analysis for Valorant players',
  keywords: ['valorant', 'aim', 'analysis', 'esports', 'gaming'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-secondary-900 text-secondary-100">
        {children}
      </body>
    </html>
  )
}
