import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AimLab VAL — Valorant Aim Analyzer',
  description: 'AI-powered aim analysis for Valorant. Identify mistakes, rank up faster.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-[#070B18] text-[#F0F1F5] antialiased">{children}</body>
    </html>
  )
}
