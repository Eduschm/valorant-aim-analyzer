'use client'

import Link from 'next/link'
import { Settings } from 'lucide-react'

export function Header() {
  return (
    <header className="h-12 bg-[#111318] border-b border-[#1F2130] px-6 flex items-center justify-end flex-shrink-0">
      <Link href="/settings" className="p-1.5 text-[#42495A] hover:text-[#7A8496] transition">
        <Settings className="w-4 h-4" />
      </Link>
    </header>
  )
}
