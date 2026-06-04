'use client'

import Link from 'next/link'
import { Settings } from 'lucide-react'

export function Header() {
  return (
    <header className="h-12 bg-val-surface border-b border-val-border px-6 flex items-center justify-end flex-shrink-0">
      <Link href="/settings" className="p-1.5 text-val-muted hover:text-val-subtle transition">
        <Settings className="w-4 h-4" />
      </Link>
    </header>
  )
}
