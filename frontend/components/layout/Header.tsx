'use client'

import Link from 'next/link'
import { Bell, User } from 'lucide-react'

export function Header() {
  return (
    <header className="bg-secondary-800 border-b border-secondary-700 px-8 py-4 flex justify-between items-center">
      <div className="flex-1"></div>
      <div className="flex items-center gap-4">
        <button className="p-2 hover:bg-secondary-700 rounded-lg transition text-secondary-300">
          <Bell className="w-5 h-5" />
        </button>
        <Link href="/settings" className="p-2 hover:bg-secondary-700 rounded-lg transition text-secondary-300">
          <User className="w-5 h-5" />
        </Link>
      </div>
    </header>
  )
}
