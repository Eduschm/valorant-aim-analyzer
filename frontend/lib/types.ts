export interface User {
  id: string
  email: string
  riotId?: string
  gameName?: string
  tagLine?: string
  createdAt: string
}

export interface Analysis {
  id: string
  userId: string
  riotId: string
  createdAt: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  stats: {
    headshotPercent: number
    adr: number
    rankDelta: string
    matchesAnalyzed: number
  }
  weaponStats: WeaponStat[]
  agentStats: AgentStat[]
  coachingReport: string
}

export interface WeaponStat {
  weapon: string
  kills: number
  accuracy: number
  headshots?: number
}

export interface AgentStat {
  agent: string
  matches: number
  winRate: number
  kills?: number
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
}
