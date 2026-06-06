'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Crosshair, Menu, X } from 'lucide-react'

/** Public marketing nav. Shared by the landing page and all standalone pages. */
const NAV = [
  { href: '/guide',   label: 'Guide' },
  { href: '/roadmap', label: 'Roadmap' },
  { href: '/pricing', label: 'Pricing' },
  { href: '/faq',     label: 'FAQ' },
]

function Logo() {
  return (
    <Link href="/" className="flex items-center gap-2">
      <span className="flex h-7 w-7 items-center justify-center clip-corner-sm bg-gradient-to-br from-val-accent to-val-accent-dark">
        <Crosshair className="h-4 w-4 text-white" />
      </span>
      <span className="font-display text-lg font-bold uppercase tracking-widest">
        <span className="text-val-accent">AimLab</span>
        <span className="text-[#F0F1F5]">VAL</span>
      </span>
    </Link>
  )
}

export function SiteHeader() {
  const pathname = usePathname()
  const [open, setOpen] = useState(false)

  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-[#1F2130] bg-[#070B18]/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
        <Logo />

        {/* Desktop nav */}
        <nav className="hidden items-center gap-7 md:flex">
          {NAV.map(({ href, label }) => {
            const active = pathname === href
            return (
              <Link
                key={href}
                href={href}
                className={`text-sm transition hover:text-[#F0F1F5] ${
                  active ? 'text-val-accent' : 'text-[#7A8496]'
                }`}
              >
                {label}
              </Link>
            )
          })}
        </nav>

        <div className="hidden items-center gap-5 md:flex">
          <Link href="/auth/signin" className="text-sm text-[#7A8496] transition hover:text-[#F0F1F5]">
            Sign in
          </Link>
          <Link
            href="/#analyze"
            className="clip-corner-sm bg-val-accent px-4 py-1.5 text-sm font-semibold text-white transition hover:bg-val-accent-dark"
          >
            Get started
          </Link>
        </div>

        {/* Mobile toggle */}
        <button
          onClick={() => setOpen(true)}
          className="p-1.5 text-[#7A8496] transition hover:text-[#F0F1F5] md:hidden"
          aria-label="Open menu"
        >
          <Menu className="h-5 w-5" />
        </button>
      </div>

      {/* Mobile drawer */}
      <AnimatePresence>
        {open && (
          <>
            <motion.div
              className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setOpen(false)}
            />
            <motion.aside
              className="fixed inset-y-0 right-0 z-50 flex w-64 flex-col gap-1 border-l border-[#1F2130] bg-[#0A0E20] p-5 md:hidden"
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', stiffness: 380, damping: 38 }}
            >
              <div className="mb-4 flex items-center justify-between">
                <Logo />
                <button
                  onClick={() => setOpen(false)}
                  className="p-1 text-[#7A8496] hover:text-[#F0F1F5]"
                  aria-label="Close menu"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              {NAV.map(({ href, label }) => (
                <Link
                  key={href}
                  href={href}
                  onClick={() => setOpen(false)}
                  className="rounded-lg px-3 py-2.5 text-sm text-[#7A8496] transition hover:bg-white/[0.03] hover:text-[#F0F1F5]"
                >
                  {label}
                </Link>
              ))}
              <div className="mt-auto space-y-2 border-t border-[#1F2130] pt-4">
                <Link
                  href="/auth/signin"
                  onClick={() => setOpen(false)}
                  className="block rounded-lg px-3 py-2.5 text-sm text-[#7A8496] transition hover:text-[#F0F1F5]"
                >
                  Sign in
                </Link>
                <Link
                  href="/#analyze"
                  onClick={() => setOpen(false)}
                  className="clip-corner-sm block bg-val-accent px-3 py-2.5 text-center text-sm font-semibold text-white transition hover:bg-val-accent-dark"
                >
                  Get started
                </Link>
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </header>
  )
}
