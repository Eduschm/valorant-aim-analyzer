import { MagicLinkForm } from '@/components/auth/MagicLinkForm'
import Link from 'next/link'

export default function SignInPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary-900 via-secondary-800 to-secondary-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-primary-400 rounded-lg mx-auto mb-4"></div>
          <h1 className="text-3xl font-bold">Welcome Back</h1>
          <p className="text-secondary-300 mt-2">Sign in to your Valorant Aim Analyzer account</p>
        </div>

        <MagicLinkForm />

        <p className="text-center text-secondary-400 mt-6">
          Don&apos;t have an account?{' '}
          <Link href="/auth/signin" className="text-primary-400 hover:text-primary-300">
            Create one with your email
          </Link>
        </p>
      </div>
    </div>
  )
}
