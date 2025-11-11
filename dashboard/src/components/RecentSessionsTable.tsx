import { useState } from 'react'
import { Session } from '../api/client'
import { formatDistanceToNow } from 'date-fns'
import SessionHoverCard from './SessionHoverCard'
import SessionDetailModal from './SessionDetailModal'

interface RecentSessionsTableProps {
  sessions: Session[]
}

export default function RecentSessionsTable({ sessions }: RecentSessionsTableProps) {
  const [hoveredSession, setHoveredSession] = useState<Session | null>(null)
  const [hoverPosition, setHoverPosition] = useState({ x: 0, y: 0 })
  const [selectedSession, setSelectedSession] = useState<Session | null>(null)

  if (!sessions || sessions.length === 0) {
    return (
      <div className="p-6 text-center text-gray-400">
        <p>No sessions found. Start using Claude Code to see your sessions here!</p>
      </div>
    )
  }

  const handleMouseEnter = (session: Session, e: React.MouseEvent) => {
    setHoveredSession(session)
    setHoverPosition({ x: e.clientX, y: e.clientY })
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (hoveredSession) {
      setHoverPosition({ x: e.clientX, y: e.clientY })
    }
  }

  const handleMouseLeave = () => {
    setHoveredSession(null)
  }

  const handleRowClick = (session: Session) => {
    setSelectedSession(session)
  }

  return (
    <>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Platform
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Interactions
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acceptance Rate
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Changes
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sessions.map((session) => (
              <tr
                key={session.id}
                className="hover:bg-gray-50 cursor-pointer transition-colors"
                onMouseEnter={(e) => handleMouseEnter(session, e)}
                onMouseMove={handleMouseMove}
                onMouseLeave={handleMouseLeave}
                onClick={() => handleRowClick(session)}
              >
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatDistanceToNow(new Date(session.started_at), { addSuffix: true })}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                    {session.platform}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {session.interaction_count}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {session.acceptance_rate ? (
                    <span className={`font-medium ${
                      session.acceptance_rate > 0.8 ? 'text-green-600' :
                      session.acceptance_rate > 0.6 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {(session.acceptance_rate * 100).toFixed(1)}%
                    </span>
                  ) : (
                    <span className="text-gray-400">N/A</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {session.total_changes}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {hoveredSession && (
        <SessionHoverCard
          session={hoveredSession}
          x={hoverPosition.x}
          y={hoverPosition.y}
        />
      )}

      {selectedSession && (
        <SessionDetailModal
          session={selectedSession}
          onClose={() => setSelectedSession(null)}
        />
      )}
    </>
  )
}

