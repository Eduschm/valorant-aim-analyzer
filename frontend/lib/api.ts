const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'

export class ApiClient {
  static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_URL}${endpoint}`
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    return response.json()
  }

  static async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  static async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  static async put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  static async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }
}

// Auth endpoints
export const authApi = {
  signin: (email: string) => ApiClient.post('/api/auth/signin', { email }),
  linkRiotId: (gameName: string, tagLine: string) =>
    ApiClient.post('/api/auth/link-riot-id', { gameName, tagLine }),
  getSession: () => ApiClient.get('/api/auth/session'),
}

// Analysis endpoints
export const analysisApi = {
  createTracker: (riotId: string) =>
    ApiClient.post('/api/analysis/tracker', { riotId }),
  getAnalysis: (id: string) =>
    ApiClient.get(`/api/analysis/${id}`),
  getHistory: () =>
    ApiClient.get('/api/analysis/history'),
}

// User endpoints
export const userApi = {
  getProfile: () => ApiClient.get('/api/user/profile'),
  updateProfile: (data: any) =>
    ApiClient.put('/api/user/profile', data),
}
