import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  saveAnalysis, getAnalyses, getLatestAnalysis,
  getAllAnalyses, clearAnalyses,
} from '../storage'

const MOCK_REPORT = (gameName = 'TestPlayer', tag = 'NA1', id = 'r1') => ({
  report_id: id,
  riot_report: { game_name: gameName, tag_line: tag, avg_headshot_pct: 22, avg_adr: 140, win_rate: 0.5, matches: [] },
  coaching: null,
})

beforeEach(() => {
  localStorage.clear()
})

describe('saveAnalysis', () => {
  it('stores an entry retrievable by riotId', () => {
    saveAnalysis(MOCK_REPORT())
    const entries = getAnalyses('TestPlayer#NA1')
    expect(entries).toHaveLength(1)
    expect(entries[0].id).toBe('r1')
  })

  it('extracts correct riot_id from report', () => {
    saveAnalysis(MOCK_REPORT('Shroud', 'EU1', 'r2'))
    const entries = getAnalyses('Shroud#EU1')
    expect(entries).toHaveLength(1)
  })

  it('prepends newest — most recent at index 0', () => {
    saveAnalysis(MOCK_REPORT('P', 'NA1', 'old'))
    saveAnalysis(MOCK_REPORT('P', 'NA1', 'new'))
    expect(getAnalyses('P#NA1')[0].id).toBe('new')
  })

  it('caps at 20 entries per riot ID', () => {
    for (let i = 0; i < 25; i++) {
      saveAnalysis(MOCK_REPORT('P', 'NA1', `r${i}`))
    }
    expect(getAnalyses('P#NA1')).toHaveLength(20)
  })
})

describe('getLatestAnalysis', () => {
  it('returns most recent entry', () => {
    saveAnalysis(MOCK_REPORT('P', 'NA1', 'r1'))
    saveAnalysis(MOCK_REPORT('P', 'NA1', 'r2'))
    expect(getLatestAnalysis('P#NA1')?.id).toBe('r2')
  })

  it('returns null when no entries', () => {
    expect(getLatestAnalysis('Nobody#NA1')).toBeNull()
  })
})

describe('getAllAnalyses', () => {
  it('flattens multiple riot IDs', () => {
    saveAnalysis(MOCK_REPORT('A', 'NA1', 'r1'))
    saveAnalysis(MOCK_REPORT('B', 'EU1', 'r2'))
    expect(getAllAnalyses()).toHaveLength(2)
  })

  it('sorts newest first', () => {
    saveAnalysis(MOCK_REPORT('P', 'NA1', 'old'))
    // Small delay to get different timestamps
    saveAnalysis(MOCK_REPORT('P', 'NA1', 'new'))
    const all = getAllAnalyses()
    expect(all[0].id).toBe('new')
  })
})

describe('clearAnalyses', () => {
  it('empties all stored data', () => {
    saveAnalysis(MOCK_REPORT())
    clearAnalyses()
    expect(getAllAnalyses()).toHaveLength(0)
  })
})

describe('error resilience', () => {
  it('handles corrupted localStorage gracefully', () => {
    localStorage.setItem('aimlab_analyses', '{invalid json}')
    expect(() => getAllAnalyses()).not.toThrow()
    expect(getAllAnalyses()).toHaveLength(0)
  })
})
