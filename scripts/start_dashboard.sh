#!/bin/bash
# Start both API server and dashboard

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DASHBOARD_DIR="$PROJECT_DIR/dashboard"

echo "Starting Blueplane Telemetry Core..."

# Check if API server is running
if ! curl -s http://localhost:7531/health > /dev/null 2>&1; then
    echo "Starting API server..."
    cd "$PROJECT_DIR"
    python scripts/run_api_server.py > /tmp/blueplane_api.log 2>&1 &
    API_PID=$!
    echo "API server started (PID: $API_PID)"
    sleep 2
else
    echo "API server already running"
fi

# Start dashboard
if [ -d "$DASHBOARD_DIR" ]; then
    echo "Starting dashboard..."
    cd "$DASHBOARD_DIR"
    npm run dev > /tmp/blueplane_dashboard.log 2>&1 &
    DASHBOARD_PID=$!
    echo "Dashboard started (PID: $DASHBOARD_PID)"
    echo ""
    echo "✅ Dashboard available at: http://localhost:3000"
    echo "✅ API available at: http://localhost:7531"
    echo ""
    echo "Logs:"
    echo "  API: /tmp/blueplane_api.log"
    echo "  Dashboard: /tmp/blueplane_dashboard.log"
else
    echo "⚠️  Dashboard directory not found. Run 'npm install' in dashboard/ first."
fi

