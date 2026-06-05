'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useState, type ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  Plus,
  Settings,
  LogOut,
  TrendingUp,
  User,
  Menu,
  X,
  Crosshair,
} from 'lucide-react'
import { clearAnalyses } from '@/lib/storage'

const NAV = [
  { href: '/dashboard',    label: 'Dashboard',    icon: LayoutDashboard },
  { href: '/analysis/new', label: 'New Analysis', icon: Plus },
  { href: '/tracker',      label: 'Tracker',      icon: TrendingUp },
  { href: '/profile',      label: 'Profile',      icon: User },
  { href: '/settings',     label: 'Settings',     icon: Settings },
]

function Logo() {
  return (
    <Link href="/" className="flex items-center gap-2 group">
      <span className="relative flex h-8 w-8 items-center justify-center clip-corner-sm bg-gradient-to-br from-[#FF4655] to-[#B8323D] shadow-red-glow-sm">
        <Crosshair className="h-4 w-4 text-white" />
      </span>
      <span className="font-display text-base font-bold tracking-widest uppercase">
        <span className="text-[#FF4655]">AimLab</span>
        <span className="text-[#F0F1F5]">VAL</span>
      </span>
    </Link>
  )
}

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname()
  return (
    <nav className="flex-1 px-3 py-4 space-y-1">
      {NAV.map(({ href, label, icon: Icon }) => {
        const active = pathname === href || pathname.startsWith(href + '/')
        return (
          <Link
            key={href}
            href={href}
            onClick={onNavigate}
            className={`relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
              active ? 'text-[#F0F1F5]' : 'text-[#7A8496] hover:text-[#F0F1F5]'
            }`}
          >
            {active && (
              <motion.span
                layoutId="active-nav"
                className="absolute inset-0 rounded-lg bg-[#FF4655]/10 border border-[#FF4655]/30"
                transition={{ type: 'spring', stiffness: 400, damping: 32 }}
              />
            )}
            {active && (
              <motion.span
                layoutId="active-bar"
                className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-[#FF4655]"
                transition={{ type: 'spring', stiffness: 400, damping: 32 }}
              />
            )}
            <Icon className="relative z-10 h-4 w-4 flex-shrink-0" />
            <span className="relative z-10 font-medium">{label}</span>
          </Link>
        )
      })}
    </nav>
  )
}

function pageTitle(pathname: string): string {
  const item = NAV.find((n) => pathname === n.href || pathname.startsWith(n.href + '/'))
  if (item) return item.label
  if (pathname.startsWith('/analysis/')) return 'Analysis Report'
  return 'AimLab VAL'
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const [mobileOpen, setMobileOpen] = useState(false)

  const handleSignOut = () => {
    clearAnalyses()
    document.cookie = 'auth_token=; Max-Age=0; path=/'
    router.push('/')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-[#07080C]">
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex w-60 flex-col flex-shrink-0 glass border-r border-[#1F2130]">
        <div className="px-5 py-5 border-b border-[#1F2130]">
          <Logo />
        </div>
        <NavLinks />
        <button
          onClick={handleSignOut}
          className="flex items-center gap-3 px-6 py-4 text-sm text-[#42495A] hover:text-[#FF4655] transition border-t border-[#1F2130]"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </aside>

      {/* Mobile drawer */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              className="fixed inset-y-0 left-0 z-50 flex w-64 flex-col glass border-r border-[#1F2130] lg:hidden"
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', stiffness: 380, damping: 38 }}
            >
              <div className="flex items-center justify-between px-5 py-5 border-b border-[#1F2130]">
                <Logo />
                <button
                  onClick={() => setMobileOpen(false)}
                  className="p-1 text-[#7A8496] hover:text-[#F0F1F5]"
                  aria-label="Close menu"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              <NavLinks onNavigate={() => setMobileOpen(false)} />
              <button
                onClick={handleSignOut}
                className="flex items-center gap-3 px-6 py-4 text-sm text-[#42495A] hover:text-[#FF4655] transition border-t border-[#1F2130]"
              >
                <LogOut className="h-4 w-4" />
                Sign out
              </button>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Main column */}
      <div className="flex flex-1 flex-col min-w-0">
        <header className="flex h-14 flex-shrink-0 items-center gap-3 border-b border-[#1F2130] bg-[#0A0B0F]/80 px-4 backdrop-blur sm:px-6">
          <button
            onClick={() => setMobileOpen(true)}
            className="p-1.5 text-[#7A8496] hover:text-[#F0F1F5] lg:hidden"
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5" />
          </button>
          <h2 className="font-display text-sm font-semibold uppercase tracking-widest text-[#F0F1F5]">
            {pageTitle(pathname)}
          </h2>
          <Link
            href="/analysis/new"
            className="ml-auto clip-corner-sm hidden items-center gap-1.5 bg-[#FF4655] px-3.5 py-1.5 text-xs font-semibold text-white transition hover:bg-[#CC3542] sm:inline-flex"
          >
            <Plus className="h-3.5 w-3.5" /> New analysis
          </Link>
        </header>
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  )
}
