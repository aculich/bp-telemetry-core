import { Session } from '../api/client'
import { format } from 'date-fns'

interface SessionDetailModalProps {
  session: Session | null
  onClose: () => void
}

export default function SessionDetailModal({ session, onClose }: SessionDetailModalProps) {
  if (!session) return null

  const duration = session.ended_at
    ? Math.round((new Date(session.ended_at).getTime() - new Date(session.started_at).getTime()) / 1000 / 60)
    : null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" onClick={onClose}></div>

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Session Details</h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-500 text-2xl font-bold"
              >
                ×
              </button>
            </div>

            <div className="space-y-6">
              {/* Header Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Session ID</label>
                  <p className="mt-1 text-sm text-gray-900 font-mono">{session.session_id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Platform</label>
                  <p className="mt-1">
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                      {session.platform}
                    </span>
                  </p>
                </div>
              </div>

              {/* Timeline */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Started</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {format(new Date(session.started_at), 'MMM d, yyyy HH:mm:ss')}
                  </p>
                </div>
                {session.ended_at && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Ended</label>
                    <p className="mt-1 text-sm text-gray-900">
                      {format(new Date(session.ended_at), 'MMM d, yyyy HH:mm:ss')}
                    </p>
                  </div>
                )}
                {duration !== null && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Duration</label>
                    <p className="mt-1 text-sm text-gray-900">{duration} minutes</p>
                  </div>
                )}
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-4 gap-4 pt-4 border-t border-gray-200">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{session.interaction_count}</div>
                  <div className="text-sm text-gray-500 mt-1">Interactions</div>
                </div>
                <div className="text-center">
                  <div className={`text-2xl font-bold ${
                    session.acceptance_rate && session.acceptance_rate > 0.8 ? 'text-green-600' :
                    session.acceptance_rate && session.acceptance_rate > 0.6 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {session.acceptance_rate ? `${(session.acceptance_rate * 100).toFixed(1)}%` : 'N/A'}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">Acceptance Rate</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{session.total_changes}</div>
                  <div className="text-sm text-gray-500 mt-1">Code Changes</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {session.total_tokens?.toLocaleString() || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">Tokens Used</div>
                </div>
              </div>

              {/* Performance Indicators */}
              {session.acceptance_rate && (
                <div className="pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Performance</h4>
                  <div className="space-y-2">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Acceptance Rate</span>
                        <span className="font-medium text-gray-900">
                          {session.acceptance_rate > 0.8 ? 'Excellent' :
                           session.acceptance_rate > 0.6 ? 'Good' : 'Needs Improvement'}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            session.acceptance_rate > 0.8 ? 'bg-green-500' :
                            session.acceptance_rate > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${session.acceptance_rate * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="button"
              onClick={onClose}
              className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none sm:ml-3 sm:w-auto sm:text-sm"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

