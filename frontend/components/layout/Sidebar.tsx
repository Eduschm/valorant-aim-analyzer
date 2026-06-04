'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Plus, Settings, LogOut } from 'lucide-react'

export function Sidebar() {
  const pathname = usePathname()

  const isActive = (href: string) => pathname === href

  return (
    <aside className="w-64 bg-secondary-800 border-r border-secondary-700 p-6 flex flex-col">
      <Link href="/dashboard" className="flex items-center gap-2 mb-8">
        <div className="w-8 h-8 bg-primary-400 rounded-lg"></div>
        <span className="font-bold text-lg">Analyzer</span>
      </Link>

      <nav className="flex-1 space-y-2">
        <Link
          href="/dashboard"
          className={`flex items-center gap-3 px-4 py-2 rounded-lg transition ${
            isActive('/dashboard')
              ? 'bg-primary-400/20 text-primary-400'
              : 'text-secondary-300 hover:bg-secondary-700'
          }`}
        >
          <LayoutDashboard className="w-5 h-5" />
          Dashboard
        </Link>
        <Link
          href="/analysis/new"
          className={`flex items-center gap-3 px-4 py-2 rounded-lg transition ${
            isActive('/analysis/new')
              ? 'bg-primary-400/20 text-primary-400'
              : 'text-secondary-300 hover:bg-secondary-700'
          }`}
        >
          <Plus className="w-5 h-5" />
          New Analysis
        </Link>
        <Link
          href="/settings"
          className={`flex items-center gap-3 px-4 py-2 rounded-lg transition ${
            isActive('/settings')
              ? 'bg-primary-400/20 text-primary-400'
              : 'text-secondary-300 hover:bg-secondary-700'
          }`}
        >
          <Settings className="w-5 h-5" />
          Settings
        </Link>
      </nav>

      <button className="flex items-center gap-3 px-4 py-2 rounded-lg text-secondary-300 hover:bg-secondary-700 w-full transition">
        <LogOut className="w-5 h-5" />
        Sign Out
      </button>
    </aside>
  )
}
