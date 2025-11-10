import axios from 'axios'

const API_BASE_URL = '/api/v1'

export interface MetricsResponse {
  realtime: Record<string, number>
  session: Record<string, number>
  tools: Record<string, number>
}

export interface Session {
  id: string
  session_id: string
  external_session_id: string
  platform: string
  started_at: string
  ended_at?: string
  interaction_count: number
  acceptance_rate?: number
  total_tokens: number
  total_changes: number
}

export interface DashboardData {
  metrics: {
    acceptance_rate: number
    time_saved_hours: number
    sessions_count: number
    productivity_score: number
  }
  trends: {
    acceptance_rate: Array<{ date: string; value: number }>
    tool_usage: Array<{ tool: string; count: number }>
    productivity_by_hour: Array<{ hour: number; value: number }>
  }
  recent_sessions: Session[]
}

class APIClient {
  private client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  async getMetrics(): Promise<MetricsResponse> {
    const response = await this.client.get<MetricsResponse>('/metrics')
    return response.data
  }

  async getSessions(limit = 50): Promise<Session[]> {
    const response = await this.client.get<Session[]>('/sessions', {
      params: { limit },
    })
    return response.data
  }

  async getSession(id: string): Promise<Session> {
    const response = await this.client.get<Session>(`/sessions/${id}`)
    return response.data
  }

  async getDashboardData(): Promise<DashboardData> {
    // For now, we'll construct this from available endpoints
    // In the future, this should be a dedicated endpoint
    const [metrics, sessions] = await Promise.all([
      this.getMetrics(),
      this.getSessions(10),
    ])

    // Calculate dashboard metrics from API data
    const acceptance_rate = metrics.session.acceptance_rate || 0
    const time_saved_hours = metrics.session.time_saved_hours || 0
    const sessions_count = sessions.length
    const productivity_score = this.calculateProductivityScore(metrics)

    return {
      metrics: {
        acceptance_rate,
        time_saved_hours,
        sessions_count,
        productivity_score,
      },
      trends: {
        acceptance_rate: [], // TODO: Implement trend endpoint
        tool_usage: this.extractToolUsage(metrics.tools),
        productivity_by_hour: [], // TODO: Implement hourly endpoint
      },
      recent_sessions: sessions,
    }
  }

  private calculateProductivityScore(metrics: MetricsResponse): number {
    // Simple scoring algorithm
    const acceptanceRate = metrics.session.acceptance_rate || 0
    const toolVariety = Object.keys(metrics.tools).length
    const baseScore = acceptanceRate * 10 // 0-10 scale
    const varietyBonus = Math.min(toolVariety * 0.2, 2) // Max 2 points
    return Math.min(baseScore + varietyBonus, 10)
  }

  private extractToolUsage(tools: Record<string, number>): Array<{ tool: string; count: number }> {
    return Object.entries(tools).map(([tool, count]) => ({
      tool,
      count: typeof count === 'number' ? count : 0,
    }))
  }
}

export const apiClient = new APIClient()

