import { Session } from '../api/client'
import { format } from 'date-fns'

interface SessionHoverCardProps {
  session: Session
  x: number
  y: number
}

export default function SessionHoverCard({ session, x, y }: SessionHoverCardProps) {
  const duration = session.ended_at
    ? Math.round((new Date(session.ended_at).getTime() - new Date(session.started_at).getTime()) / 1000 / 60)
    : null

  return (
    <div
      className="fixed z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-4 min-w-[300px] pointer-events-none"
      style={{ left: `${x + 10}px`, top: `${y - 10}px` }}
    >
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h4 className="font-semibold text-gray-900">Session Details</h4>
          <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
            {session.platform}
          </span>
        </div>
        
        <div className="text-sm text-gray-600 space-y-1">
          <div className="flex justify-between">
            <span>Started:</span>
            <span className="text-gray-900">{format(new Date(session.started_at), 'MMM d, yyyy HH:mm')}</span>
          </div>
          {session.ended_at && (
            <div className="flex justify-between">
              <span>Ended:</span>
              <span className="text-gray-900">{format(new Date(session.ended_at), 'MMM d, yyyy HH:mm')}</span>
            </div>
          )}
          {duration !== null && (
            <div className="flex justify-between">
              <span>Duration:</span>
              <span className="text-gray-900">{duration} minutes</span>
            </div>
          )}
        </div>

        <div className="border-t border-gray-200 pt-2 mt-2">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-600">Interactions</div>
              <div className="text-lg font-semibold text-gray-900">{session.interaction_count}</div>
            </div>
            <div>
              <div className="text-gray-600">Code Changes</div>
              <div className="text-lg font-semibold text-gray-900">{session.total_changes}</div>
            </div>
            <div>
              <div className="text-gray-600">Acceptance Rate</div>
              <div className={`text-lg font-semibold ${
                session.acceptance_rate && session.acceptance_rate > 0.8 ? 'text-green-600' :
                session.acceptance_rate && session.acceptance_rate > 0.6 ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {session.acceptance_rate ? `${(session.acceptance_rate * 100).toFixed(1)}%` : 'N/A'}
              </div>
            </div>
            <div>
              <div className="text-gray-600">Tokens Used</div>
              <div className="text-lg font-semibold text-gray-900">{session.total_tokens?.toLocaleString() || 'N/A'}</div>
            </div>
          </div>
        </div>

        <div className="pt-2 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            Click to view full details
          </div>
        </div>
      </div>
    </div>
  )
}

