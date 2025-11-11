import { useEffect, useState } from 'react'
import { apiClient, DashboardData } from '../api/client'
// Icons removed - using emoji/text instead

interface Pattern {
  title: string
  description: string
  type: 'positive' | 'negative' | 'neutral'
  impact: 'high' | 'medium' | 'low'
  recommendation?: string
}

export default function Patterns() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [patterns, setPatterns] = useState<Pattern[]>([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const dashboardData = await apiClient.getDashboardData()
      setData(dashboardData)
      analyzePatterns(dashboardData)
    } catch (err) {
      console.error('Failed to load patterns:', err)
    } finally {
      setLoading(false)
    }
  }

  const analyzePatterns = (data: DashboardData) => {
    const detectedPatterns: Pattern[] = []

    // Pattern 1: High Acceptance Rate
    if (data.metrics.acceptance_rate > 0.8) {
      detectedPatterns.push({
        title: 'Excellent Acceptance Rate',
        description: `You're accepting ${(data.metrics.acceptance_rate * 100).toFixed(1)}% of AI suggestions, indicating highly effective prompts and valuable AI assistance.`,
        type: 'positive',
        impact: 'high',
        recommendation: 'Continue your current approach. Your prompts are well-crafted and AI is providing valuable assistance.'
      })
    } else if (data.metrics.acceptance_rate < 0.6) {
      detectedPatterns.push({
        title: 'Low Acceptance Rate',
        description: `Your acceptance rate is ${(data.metrics.acceptance_rate * 100).toFixed(1)}%, suggesting room for improvement in prompt quality or AI tool selection.`,
        type: 'negative',
        impact: 'high',
        recommendation: 'Consider refining your prompts, being more specific about requirements, or trying different AI tools that better match your workflow.'
      })
    }

    // Pattern 2: Tool Usage Distribution
    const toolUsage = data.trends.tool_usage || []
    if (toolUsage.length > 0) {
      const editUsage = toolUsage.find(t => t.tool === 'Edit')?.count || 0
      const totalUsage = toolUsage.reduce((sum, t) => sum + t.count, 0)
      const editPercentage = totalUsage > 0 ? (editUsage / totalUsage) * 100 : 0

      if (editPercentage > 70) {
        detectedPatterns.push({
          title: 'Heavy Edit Tool Usage',
          description: `You're using Edit tools ${editPercentage.toFixed(0)}% of the time. Consider using ReadFile and Search more to understand code before editing.`,
          type: 'neutral',
          impact: 'medium',
          recommendation: 'Try reading files and searching for patterns before making edits. This workflow often leads to better acceptance rates.'
        })
      } else if (toolUsage.length >= 3 && editPercentage < 50) {
        detectedPatterns.push({
          title: 'Balanced Tool Usage',
          description: 'You\'re using a good variety of tools, which suggests comprehensive AI assistance.',
          type: 'positive',
          impact: 'medium',
          recommendation: 'Maintain this balanced approach. Tool variety often correlates with better outcomes.'
        })
      }
    }

    // Pattern 3: Session Frequency
    if (data.metrics.sessions_count > 100) {
      detectedPatterns.push({
        title: 'High Session Frequency',
        description: `You've had ${data.metrics.sessions_count} sessions, showing consistent AI-assisted coding.`,
        type: 'positive',
        impact: 'low',
        recommendation: 'Your consistent usage suggests AI assistance is becoming a core part of your workflow.'
      })
    }

    // Pattern 4: Productivity Score
    if (data.metrics.productivity_score > 8.5) {
      detectedPatterns.push({
        title: 'High Productivity Score',
        description: `Your productivity score of ${data.metrics.productivity_score.toFixed(1)}/10 indicates excellent AI-assisted coding efficiency.`,
        type: 'positive',
        impact: 'high',
        recommendation: 'You\'re maximizing the value from AI assistance. Consider sharing your approach with your team.'
      })
    }

    // Pattern 5: Time Saved
    if (data.metrics.time_saved_hours > 20) {
      detectedPatterns.push({
        title: 'Significant Time Savings',
        description: `You've saved ${data.metrics.time_saved_hours.toFixed(1)} hours through AI assistance this week.`,
        type: 'positive',
        impact: 'high',
        recommendation: `At a typical hourly rate, this represents substantial value. Consider calculating ROI to justify continued tool investment.`
      })
    }

    // Pattern 6: Session-level insights
    if (data.recent_sessions.length > 0) {
      const highAcceptanceSessions = data.recent_sessions.filter(s => s.acceptance_rate && s.acceptance_rate > 0.9)
      const lowAcceptanceSessions = data.recent_sessions.filter(s => s.acceptance_rate && s.acceptance_rate < 0.6)

      if (highAcceptanceSessions.length > lowAcceptanceSessions.length * 2) {
        detectedPatterns.push({
          title: 'Consistently High-Performing Sessions',
          description: 'Most of your recent sessions show high acceptance rates, indicating consistent effectiveness.',
          type: 'positive',
          impact: 'medium',
          recommendation: 'Review what makes your high-performing sessions successful and replicate those patterns.'
        })
      }
    }

    setPatterns(detectedPatterns)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Analyzing patterns...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Patterns & Insights</h2>
        <p className="text-gray-600 mt-1">Discover productivity patterns and actionable recommendations</p>
      </div>

      {patterns.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <span className="text-6xl mb-4 block">💡</span>
          <p className="text-gray-500">No patterns detected yet. Continue using AI assistance to generate insights.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {patterns.map((pattern, index) => (
            <div
              key={index}
              className={`bg-white rounded-lg shadow p-6 border-l-4 ${
                pattern.type === 'positive' ? 'border-green-500' :
                pattern.type === 'negative' ? 'border-red-500' : 'border-yellow-500'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    {pattern.type === 'positive' ? (
                      <span className="text-green-500 text-xl">📈</span>
                    ) : pattern.type === 'negative' ? (
                      <span className="text-red-500 text-xl">📉</span>
                    ) : (
                      <span className="text-yellow-500 text-xl">🎯</span>
                    )}
                    <h3 className="text-lg font-semibold text-gray-900">{pattern.title}</h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      pattern.impact === 'high' ? 'bg-red-100 text-red-800' :
                      pattern.impact === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {pattern.impact} impact
                    </span>
                  </div>
                  <p className="text-gray-600 mb-3">{pattern.description}</p>
                  {pattern.recommendation && (
                      <div className="bg-gray-50 rounded-lg p-4 mt-4">
                        <div className="flex items-start space-x-2">
                          <span className="text-yellow-500 text-xl mt-0.5 flex-shrink-0">💡</span>
                        <div>
                          <p className="text-sm font-medium text-gray-900 mb-1">Recommendation</p>
                          <p className="text-sm text-gray-700">{pattern.recommendation}</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary Stats */}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center space-x-2">
              <span className="text-blue-500 text-xl">🎯</span>
              <div>
                <p className="text-sm text-gray-500">Productivity Score</p>
                <p className="text-2xl font-bold text-gray-900">{data.metrics.productivity_score.toFixed(1)}/10</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center space-x-2">
              <span className="text-green-500 text-xl">⏰</span>
              <div>
                <p className="text-sm text-gray-500">Time Saved</p>
                <p className="text-2xl font-bold text-gray-900">{data.metrics.time_saved_hours.toFixed(1)}h</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center space-x-2">
              <span className="text-purple-500 text-xl">📈</span>
              <div>
                <p className="text-sm text-gray-500">Acceptance Rate</p>
                <p className="text-2xl font-bold text-gray-900">{(data.metrics.acceptance_rate * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
