import { AGENT_ASSETS, RANK_ASSETS } from '@/lib/generated/valorant-assets'

/** Resolve a Valorant agent name to its downloaded icon path, or null if unknown. */
export function agentIcon(name?: string | null): string | null {
  if (!name) return null
  const direct = AGENT_ASSETS[name]
  if (direct) return direct.icon
  const lower = name.trim().toLowerCase()
  for (const key of Object.keys(AGENT_ASSETS)) {
    if (key.toLowerCase() === lower) return AGENT_ASSETS[key].icon
  }
  return null
}

export function agentRole(name?: string | null): string | null {
  if (!name) return null
  const direct = AGENT_ASSETS[name]
  if (direct) return direct.role || null
  const lower = name.trim().toLowerCase()
  for (const key of Object.keys(AGENT_ASSETS)) {
    if (key.toLowerCase() === lower) return AGENT_ASSETS[key].role || null
  }
  return null
}

/** Resolve a rank label (e.g. "Gold 2", "Immortal 3", "Radiant") to its tier icon. */
export function rankIcon(rank?: string | null): string | null {
  if (!rank) return null
  const direct = RANK_ASSETS[rank]
  if (direct) return direct.icon
  const lower = rank.trim().toLowerCase()
  for (const key of Object.keys(RANK_ASSETS)) {
    if (key.toLowerCase() === lower) return RANK_ASSETS[key].icon
  }
  return null
}
