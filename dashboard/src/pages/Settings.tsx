import { useState } from 'react'
// Icons removed - using emoji/text instead

export default function Settings() {
  const [settings, setSettings] = useState({
    refreshInterval: 30,
    notifications: true,
    theme: 'light',
    goalAcceptanceRate: 85,
    goalTimeSaved: 5,
    exportFormat: 'json'
  })

  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    // In a real app, this would save to localStorage or backend
    localStorage.setItem('dashboardSettings', JSON.stringify(settings))
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const handleExport = () => {
    // In a real app, this would export data
    alert('Export functionality coming soon!')
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
        <p className="text-gray-600 mt-1">Customize your dashboard preferences</p>
      </div>

      {/* General Settings */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">General</h3>
        </div>
        <div className="px-6 py-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Auto-refresh Interval (seconds)
            </label>
            <input
              type="number"
              min="10"
              max="300"
              value={settings.refreshInterval}
              onChange={(e) => setSettings({ ...settings, refreshInterval: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="mt-1 text-sm text-gray-500">Dashboard will refresh automatically every {settings.refreshInterval} seconds</p>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-gray-700">Enable Notifications</label>
              <p className="text-sm text-gray-500">Get notified about important metrics</p>
            </div>
            <button
              onClick={() => setSettings({ ...settings, notifications: !settings.notifications })}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                settings.notifications ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  settings.notifications ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* Goals */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center space-x-2">
          <span className="text-gray-500 text-xl">🎯</span>
          <h3 className="text-lg font-medium text-gray-900">Goals</h3>
        </div>
        <div className="px-6 py-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Acceptance Rate (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={settings.goalAcceptanceRate}
              onChange={(e) => setSettings({ ...settings, goalAcceptanceRate: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="mt-1 text-sm text-gray-500">Set your target acceptance rate goal</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Time Saved (hours per week)
            </label>
            <input
              type="number"
              min="0"
              max="40"
              value={settings.goalTimeSaved}
              onChange={(e) => setSettings({ ...settings, goalTimeSaved: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="mt-1 text-sm text-gray-500">Set your weekly time savings goal</p>
          </div>
        </div>
      </div>

      {/* Appearance */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center space-x-2">
          <span className="text-gray-500 text-xl">🎨</span>
          <h3 className="text-lg font-medium text-gray-900">Appearance</h3>
        </div>
        <div className="px-6 py-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Theme</label>
          <select
            value={settings.theme}
            onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="light">Light</option>
            <option value="dark">Dark (Coming Soon)</option>
            <option value="auto">Auto</option>
          </select>
        </div>
      </div>

      {/* Data Export */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center space-x-2">
          <span className="text-gray-500 text-xl">📥</span>
          <h3 className="text-lg font-medium text-gray-900">Data Export</h3>
        </div>
        <div className="px-6 py-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Export Format</label>
            <select
              value={settings.exportFormat}
              onChange={(e) => setSettings({ ...settings, exportFormat: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="json">JSON</option>
              <option value="csv">CSV</option>
              <option value="pdf">PDF (Coming Soon)</option>
            </select>
          </div>
          <button
            onClick={handleExport}
            className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center justify-center space-x-2"
          >
            <span>📥</span>
            <span>Export Data</span>
          </button>
        </div>
      </div>

      {/* Privacy Notice */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <span className="text-green-600 text-xl mt-0.5">🔒</span>
          <div>
            <h4 className="text-sm font-medium text-green-900 mb-1">Privacy First</h4>
            <p className="text-sm text-green-700">
              All your data stays local. No data is sent to external servers. Your privacy is guaranteed.
            </p>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className={`px-6 py-2 rounded-lg flex items-center space-x-2 ${
            saved
              ? 'bg-green-600 text-white'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          <span>{saved ? '✅' : '💾'}</span>
          <span>{saved ? 'Saved!' : 'Save Settings'}</span>
        </button>
      </div>
    </div>
  )
}
