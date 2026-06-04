/**
 * localStorage persistence for analysis results.
 * Keyed by Riot ID — tracker and profile pages read from here.
 * Max 20 entries per Riot ID to keep storage bounded.
 */

const KEY = 'aimlab_analyses'
const MAX_PER_ID = 20

export interface StoredAnalysis {
  id:         string
  riot_id:    string
  saved_at:   string   // ISO timestamp
  riot_report: Record<string, any> | null
  coaching:    Record<string, any> | null
}

function load(): Record<string, StoredAnalysis[]> {
  if (typeof window === 'undefined') return {}
  try {
    return JSON.parse(localStorage.getItem(KEY) || '{}')
  } catch {
    return {}
  }
}

function save(data: Record<string, StoredAnalysis[]>) {
  if (typeof window === 'undefined') return
  localStorage.setItem(KEY, JSON.stringify(data))
}

export function saveAnalysis(report: { report_id: string; riot_report: any; coaching: any }) {
  const riotId = report.riot_report?.game_name && report.riot_report?.tag_line
    ? `${report.riot_report.game_name}#${report.riot_report.tag_line}`
    : 'unknown'

  const entry: StoredAnalysis = {
    id:          report.report_id,
    riot_id:     riotId,
    saved_at:    new Date().toISOString(),
    riot_report: report.riot_report,
    coaching:    report.coaching,
  }

  const all = load()
  const existing = all[riotId] || []
  // Prepend newest, cap at MAX_PER_ID
  all[riotId] = [entry, ...existing].slice(0, MAX_PER_ID)
  save(all)
}

export function getAnalyses(riotId: string): StoredAnalysis[] {
  return load()[riotId] || []
}

export function getLatestAnalysis(riotId: string): StoredAnalysis | null {
  return getAnalyses(riotId)[0] || null
}

export function getAllAnalyses(): StoredAnalysis[] {
  const all = load()
  return Object.values(all)
    .flat()
    .sort((a, b) => new Date(b.saved_at).getTime() - new Date(a.saved_at).getTime())
}

export function clearAnalyses() {
  if (typeof window !== 'undefined') localStorage.removeItem(KEY)
}
