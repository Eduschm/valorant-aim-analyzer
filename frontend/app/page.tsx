import Link from 'next/link'
import { ArrowRight, Target, TrendingUp, Zap } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0A0B0F]">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-[#1F2130] bg-[#0A0B0F]/95 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto px-6 h-13 flex items-center justify-between">
          <span className="font-display text-lg font-bold tracking-widest text-[#FF4655] uppercase">
            AimLab<span className="text-[#F0F1F5]">VAL</span>
          </span>
          <div className="flex items-center gap-5">
            <Link href="/auth/signin" className="text-[#7A8496] text-sm hover:text-[#F0F1F5] transition">Sign in</Link>
            <Link href="/analysis/new"
              className="clip-corner-sm bg-[#FF4655] text-white text-sm font-semibold px-4 py-1.5 hover:bg-[#CC3542] transition">
              Get started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-6 pt-32 pb-20">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 border border-[#1F2130] text-[#42495A] text-xs uppercase tracking-widest px-3 py-1 mb-8">
            <span className="w-1.5 h-1.5 bg-[#FF4655] rounded-full pulse-red" />
            AI coaching · Riot API data · Free to start
          </div>

          <h1 className="font-display text-5xl md:text-6xl font-bold leading-tight tracking-tight mb-5">
            Understand why you<br />
            <span className="text-[#FF4655]">lose gunfights.</span>
          </h1>

          <p className="text-[#7A8496] text-lg mb-8 max-w-lg leading-relaxed">
            Paste your Riot ID. We pull your last 20 matches, analyse your aim patterns,
            and give you a direct coaching report — specific numbers, specific fixes.
          </p>

          <Link href="/analysis/new"
            className="clip-corner inline-flex items-center gap-2 bg-[#FF4655] text-white font-semibold px-6 py-3 hover:bg-[#CC3542] transition shadow-red-glow text-sm">
            Analyze my aim
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* Divider */}
      <div className="max-w-5xl mx-auto px-6">
        <div className="h-px bg-[#1F2130]" />
      </div>

      {/* Stats */}
      <section className="max-w-5xl mx-auto px-6 py-10">
        <div className="grid grid-cols-3 gap-0 divide-x divide-[#1F2130]">
          {[
            { n: '20',   label: 'matches per report' },
            { n: '6',    label: 'mistake types detected' },
            { n: '<30s', label: 'report generation time' },
          ].map(({ n, label }) => (
            <div key={label} className="px-8 py-2 first:pl-0">
              <div className="font-display text-3xl font-bold text-[#FF4655]">{n}</div>
              <div className="text-[#42495A] text-xs mt-0.5">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-5xl mx-auto px-6 pb-24">
        <div className="h-px bg-[#1F2130] mb-8" />
        <div className="grid md:grid-cols-3 gap-px bg-[#1F2130]">
          {[
            {
              icon: Target,
              title: 'Aim analysis',
              body: 'Overshoot, undershoot, body-not-head, wrong target, movement errors. Each classified, each scored by impact on your performance.',
            },
            {
              icon: TrendingUp,
              title: 'Riot stats',
              body: 'Your last 20 ranked matches via the official Riot API. Headshot %, ADR, win rate, rank trajectory, top agent and weapon.',
            },
            {
              icon: Zap,
              title: 'AI coaching',
              body: 'Your data fed directly into Claude. Specific numbers, specific problems, specific fixes — not generic tips you\'ve read a hundred times.',
            },
          ].map(({ icon: Icon, title, body }) => (
            <div key={title} className="bg-[#111318] p-8 group hover:bg-[#181A22] transition">
              <Icon className="w-5 h-5 text-[#FF4655] mb-5" />
              <h3 className="font-display text-lg font-bold mb-2 tracking-wide">{title}</h3>
              <p className="text-[#7A8496] text-sm leading-relaxed">{body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#1F2130] py-6 px-6 flex items-center justify-between max-w-5xl mx-auto text-[#42495A] text-xs">
        <span>AimLab VAL</span>
        <span>Not affiliated with Riot Games · Valorant is a trademark of Riot Games.</span>
      </footer>
    </div>
  )
}
