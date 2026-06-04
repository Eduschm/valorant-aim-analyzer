import { RiotIdLinkForm } from '@/components/auth/RiotIdLinkForm'

export default function LinkRiotIdPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary-900 via-secondary-800 to-secondary-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-accent-400 rounded-lg mx-auto mb-4"></div>
          <h1 className="text-3xl font-bold">Link Your Riot ID</h1>
          <p className="text-secondary-300 mt-2">Connect your Valorant account to start analyzing</p>
        </div>

        <RiotIdLinkForm />
      </div>
    </div>
  )
}
