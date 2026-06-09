/**
 * API client for the FastAPI backend.
 * All endpoints match services/api/main.py routes.
 *
 * MOCK_MODE=true  → returns fixture data, no backend needed
 * MOCK_MODE=false → calls real FastAPI at NEXT_PUBLIC_API_URL
 */

import { MOCK_REPORT } from './mock/analysis'
import { logger } from './logger'

const API_URL   = process.env.NEXT_PUBLIC_API_URL  || 'http://localhost:8000'
export function isMockMode(): boolean {
  if (typeof window !== 'undefined') {
    const demoCookie = document.cookie.split('; ').find(row => row.startsWith('demo_mode='))
    if (demoCookie) {
      return demoCookie.split('=')[1] === 'true'
    }
    const stored = localStorage.getItem('aimlab_demo_mode')
    if (stored !== null) {
      return stored === 'true'
    }
  }
  return process.env.NEXT_PUBLIC_MOCK_MODE === 'true'
}

// --------------------------------------------------------------------------
// Base request
// --------------------------------------------------------------------------

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_URL}${endpoint}`
  logger.debug('API request', options.method || 'GET', url)
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const body = await res.text()
    logger.error('API error', res.status, url, body)
    throw new Error(`API ${res.status}: ${body}`)
  }
  const json = await res.json()
  logger.debug('API response', url, json)
  return json
}

// --------------------------------------------------------------------------
// Analysis
// --------------------------------------------------------------------------

export interface AnalyzeResponse {
  report_id: string
  status: 'queued' | 'processing' | 'done' | 'error'
}

export interface ReportResponse {
  report_id:   string
  status:      'queued' | 'processing' | 'done' | 'error'
  riot_report: Record<string, unknown> | null
  cv_report:   Record<string, unknown> | null
  coaching:    Record<string, unknown> | null
  error:       string | null
}

export const analysisApi = {
  /** Submit a Riot ID for analysis. Returns report_id to poll. */
  submit: async (riot_id: string): Promise<AnalyzeResponse> => {
    if (isMockMode()) {
      await new Promise(r => setTimeout(r, 800))
      return { report_id: 'mock-001', status: 'done' }
    }
    return request<AnalyzeResponse>('/api/v1/analyze', {
      method: 'POST',
      body: JSON.stringify({ riot_id }),
    })
  },

  /** Poll for report status + results. */
  getReport: async (report_id: string): Promise<ReportResponse> => {
    if (isMockMode()) {
      await new Promise(r => setTimeout(r, 400))
      return {
        report_id,
        status: 'done',
        riot_report: MOCK_REPORT.riot_report as Record<string, unknown>,
        cv_report:   null,
        coaching:    MOCK_REPORT.coaching   as Record<string, unknown>,
        error:       null,
      }
    }
    return request<ReportResponse>(`/api/v1/report/${report_id}`)
  },
}

// --------------------------------------------------------------------------
// Auth
// --------------------------------------------------------------------------

export const authApi = {
  /** Request a magic link email. */
  requestMagicLink: async (email: string): Promise<{ message: string }> => {
    if (isMockMode()) return { message: 'Check your email (mock mode)' }
    return request('/api/v1/auth/magic-link', {
      method: 'POST',
      body: JSON.stringify({ email }),
    })
  },

  /** Link a Riot ID to the authenticated account. */
  linkRiotId: async (riot_id: string): Promise<{ message: string }> => {
    if (isMockMode()) return { message: 'Riot ID linked (mock mode)' }
    return request('/api/v1/auth/riot-id', {
      method: 'POST',
      body: JSON.stringify({ riot_id }),
    })
  },
}
