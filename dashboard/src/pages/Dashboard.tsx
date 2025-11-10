import { useEffect, useState } from 'react'
import { apiClient, DashboardData } from '../api/client'
import MetricCard from '../components/MetricCard'
import AcceptanceRateChart from '../components/AcceptanceRateChart'
import ToolUsageChart from '../components/ToolUsageChart'
import RecentSessionsTable from '../components/RecentSessionsTable'

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const dashboardData = await apiClient.getDashboardData()
      setData(dashboardData)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error: {error}</p>
        <button
          onClick={loadData}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    )
  }

  if (!data) {
    return null
  }

  const { metrics, trends, recent_sessions } = data

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Personal Dashboard</h2>
        <p className="text-gray-600 mt-1">Your AI-assisted coding productivity insights</p>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Acceptance Rate"
          value={`${(metrics.acceptance_rate * 100).toFixed(1)}%`}
          trend={metrics.acceptance_rate > 0.8 ? 'up' : metrics.acceptance_rate > 0.6 ? 'neutral' : 'down'}
          subtitle="AI suggestions accepted"
          color={metrics.acceptance_rate > 0.8 ? 'green' : metrics.acceptance_rate > 0.6 ? 'yellow' : 'red'}
        />
        <MetricCard
          title="Time Saved"
          value={`${metrics.time_saved_hours.toFixed(1)}h`}
          trend="up"
          subtitle="This week"
          color="green"
        />
        <MetricCard
          title="Sessions"
          value={metrics.sessions_count.toString()}
          trend="up"
          subtitle="This month"
          color="blue"
        />
        <MetricCard
          title="Productivity Score"
          value={metrics.productivity_score.toFixed(1)}
          trend="up"
          subtitle="Out of 10"
          color="green"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Acceptance Rate Trend</h3>
          <AcceptanceRateChart data={trends.acceptance_rate} />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Tool Usage</h3>
          <ToolUsageChart data={trends.tool_usage} />
        </div>
      </div>

      {/* Recent Sessions */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Sessions</h3>
        </div>
        <RecentSessionsTable sessions={recent_sessions} />
      </div>
    </div>
  )
}

