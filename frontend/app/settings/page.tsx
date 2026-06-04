'use client'

export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-secondary-900 p-8">
      <div className="max-w-2xl">
        <h1 className="text-3xl font-bold mb-8">Settings</h1>

        <div className="bg-surface-500 border border-secondary-700 rounded-lg p-8">
          <h2 className="text-xl font-semibold mb-4">Account</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-secondary-300 text-sm mb-2">Email</label>
              <input type="email" value="user@example.com" disabled className="w-full bg-secondary-700 border border-secondary-600 rounded px-3 py-2 text-secondary-100 disabled:opacity-50" />
            </div>
            <div>
              <label className="block text-secondary-300 text-sm mb-2">Riot ID</label>
              <input type="text" value="Edu#1234" disabled className="w-full bg-secondary-700 border border-secondary-600 rounded px-3 py-2 text-secondary-100 disabled:opacity-50" />
            </div>
          </div>

          <button className="mt-6 bg-primary-400 text-secondary-900 px-4 py-2 rounded-lg font-semibold hover:bg-primary-500 transition">
            Sign Out
          </button>
        </div>
      </div>
    </div>
  )
}
