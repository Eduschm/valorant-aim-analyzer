import Link from 'next/link'
import { ArrowRight, BarChart3, Zap, TrendingUp } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-secondary-900 via-secondary-900 to-secondary-800">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-secondary-900/95 backdrop-blur border-b border-secondary-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-400 rounded-lg"></div>
              <span className="font-bold text-lg">Valorant Aim Analyzer</span>
            </div>
            <div className="flex gap-4">
              <Link href="/auth/signin" className="text-secondary-100 hover:text-primary-400 transition">
                Sign In
              </Link>
              <Link href="/auth/signin" className="bg-primary-400 text-secondary-900 px-4 py-2 rounded-lg font-semibold hover:bg-primary-500 transition">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
        <div className="text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
            Unlock Your True Aim Potential
          </h1>
          <p className="text-xl text-secondary-300 mb-8 max-w-2xl mx-auto">
            Get AI-powered insights into your Valorant gameplay. Track your aim patterns, identify weaknesses, and get personalized coaching recommendations.
          </p>
          <Link href="/auth/signin" className="inline-flex items-center gap-2 bg-primary-400 text-secondary-900 px-8 py-3 rounded-lg font-semibold hover:bg-primary-500 transition">
            Start Free Analysis
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-8 mt-24">
          <div className="bg-surface-500 border border-secondary-700 p-8 rounded-lg hover:border-primary-400 transition">
            <BarChart3 className="w-12 h-12 text-accent-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Detailed Stats</h3>
            <p className="text-secondary-300">Headshot percentage, ADR, weapon efficiency, and agent performance breakdowns.</p>
          </div>
          <div className="bg-surface-500 border border-secondary-700 p-8 rounded-lg hover:border-primary-400 transition">
            <Zap className="w-12 h-12 text-primary-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Real-time Insights</h3>
            <p className="text-secondary-300">Instant analysis of your last matches powered by advanced AI algorithms.</p>
          </div>
          <div className="bg-surface-500 border border-secondary-700 p-8 rounded-lg hover:border-primary-400 transition">
            <TrendingUp className="w-12 h-12 text-accent-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Track Progress</h3>
            <p className="text-secondary-300">Monitor your improvement over time with comprehensive performance history.</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-secondary-800 py-8 text-center text-secondary-400">
        <p>&copy; 2024 Valorant Aim Analyzer. All rights reserved.</p>
      </footer>
    </div>
  )
}
