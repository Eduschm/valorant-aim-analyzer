import { create } from 'zustand'

interface User {
  id: string
  email: string
  riotId: string
  gameName: string
  tagLine: string
}

interface AuthStore {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  setUser: (user: User | null) => void
  setLoading: (loading: boolean) => void
  logout: () => void
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isLoading: false,
  isAuthenticated: false,
  setUser: (user) =>
    set({
      user,
      isAuthenticated: !!user,
    }),
  setLoading: (isLoading) => set({ isLoading }),
  logout: () =>
    set({
      user: null,
      isAuthenticated: false,
    }),
}))

interface AnalysisState {
  currentAnalysis: any | null
  isLoading: boolean
  setCurrentAnalysis: (analysis: any) => void
  setLoading: (loading: boolean) => void
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  currentAnalysis: null,
  isLoading: false,
  setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),
  setLoading: (isLoading) => set({ isLoading }),
}))
