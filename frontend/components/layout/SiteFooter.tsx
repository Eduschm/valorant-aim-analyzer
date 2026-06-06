import Link from 'next/link'
import { Crosshair } from 'lucide-react'

const COLUMNS: { title: string; links: { href: string; label: string }[] }[] = [
  {
    title: 'Product',
    links: [
      { href: '/#analyze', label: 'Analyze my aim' },
      { href: '/tracker',  label: 'Demo tracker' },
      { href: '/pricing',  label: 'Pricing' },
    ],
  },
  {
    title: 'Learn',
    links: [
      { href: '/guide',   label: 'Guide' },
      { href: '/roadmap', label: 'Roadmap' },
      { href: '/faq',     label: 'FAQ' },
    ],
  },
  {
    title: 'Account',
    links: [
      { href: '/auth/signin', label: 'Sign in' },
      { href: '/dashboard',   label: 'Dashboard' },
    ],
  },
]

export function SiteFooter() {
  return (
    <footer className="relative border-t border-[#1F2130]">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <div className="grid gap-10 sm:grid-cols-2 md:grid-cols-4">
          <div>
            <Link href="/" className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center clip-corner-sm bg-gradient-to-br from-val-accent to-val-accent-dark">
                <Crosshair className="h-4 w-4 text-white" />
              </span>
              <span className="font-display text-lg font-bold uppercase tracking-widest">
                <span className="text-val-accent">AimLab</span>
                <span className="text-[#F0F1F5]">VAL</span>
              </span>
            </Link>
            <p className="mt-3 max-w-xs text-sm leading-relaxed text-[#42495A]">
              AI aim coaching for Valorant. Paste your Riot ID, get a numbers-specific report.
            </p>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.title}>
              <p className="mb-3 text-xs uppercase tracking-widest text-[#42495A]">{col.title}</p>
              <ul className="space-y-2">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link href={l.href} className="text-sm text-[#7A8496] transition hover:text-[#F0F1F5]">
                      {l.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-10 flex flex-col items-center justify-between gap-2 border-t border-[#1F2130] pt-6 text-xs text-[#42495A] sm:flex-row">
          <span className="font-display uppercase tracking-widest">AimLab VAL</span>
          <span>Not affiliated with Riot Games. Valorant is a trademark of Riot Games.</span>
        </div>
      </div>
    </footer>
  )
}
