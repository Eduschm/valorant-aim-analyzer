'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { LayoutDashboard, Plus, Settings, LogOut, TrendingUp, User } from 'lucide-react'
import { clearAnalyses } from '@/lib/storage'

const NAV = [
  { href: '/dashboard',    label: 'Dashboard',    icon: LayoutDashboard },
  { href: '/analysis/new', label: 'New Analysis', icon: Plus },
  { href: '/tracker',      label: 'Tracker',      icon: TrendingUp },
  { href: '/profile',      label: 'Profile',      icon: User },
  { href: '/settings',     label: 'Settings',     icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const router   = useRouter()

  const handleSignOut = () => {
    clearAnalyses()
    document.cookie = 'auth_token=; Max-Age=0; path=/'
    router.push('/')
  }

  return (
    <aside className="w-56 bg-[#111318] border-r border-[#1F2130] flex flex-col flex-shrink-0">

      {/* Logo */}
      <Link href="/" className="px-6 py-5 border-b border-[#1F2130]">
        <span className="font-display text-base font-bold tracking-widest text-[#FF4655] uppercase">
          AimLab<span className="text-[#F0F1F5]">VAL</span>
        </span>
      </Link>

      {/* Nav */}
      <nav className="flex-1 py-4">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + '/')
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-6 py-2.5 text-sm transition
                ${active
                  ? 'border-l-2 border-[#FF4655] text-[#F0F1F5] bg-[#181A22]'
                  : 'border-l-2 border-transparent text-[#7A8496] hover:text-[#F0F1F5] hover:bg-[#181A22]'
                }`}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Sign out */}
      <button
        onClick={handleSignOut}
        className="flex items-center gap-3 px-6 py-4 text-sm text-[#42495A] hover:text-[#7A8496] transition border-t border-[#1F2130]"
      >
        <LogOut className="w-4 h-4" />
        Sign out
      </button>
    </aside>
  )
}
