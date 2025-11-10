# Blueplane Telemetry Dashboard

React-based web dashboard for visualizing AI-assisted coding telemetry.

## Features

- **Personal Dashboard**: Productivity metrics, acceptance rates, tool usage
- **Session Explorer**: Browse and analyze coding sessions
- **Pattern Insights**: Discover productivity patterns
- **Real-time Updates**: WebSocket integration for live metrics

## Setup

### Prerequisites

- Node.js 18+ and npm
- Python backend running (see main README)

### Installation

```bash
cd dashboard
npm install
```

### Development

```bash
npm run dev
```

Dashboard will be available at http://localhost:3000

### Build

```bash
npm run build
```

## Architecture

- **React 18** with TypeScript
- **Vite** for build tooling
- **Recharts** for data visualization
- **Tailwind CSS** for styling
- **React Router** for navigation

## API Integration

The dashboard connects to the FastAPI backend at `http://localhost:7531/api/v1`:

- `GET /api/v1/metrics` - Current metrics
- `GET /api/v1/sessions` - List sessions
- `GET /api/v1/sessions/{id}` - Session details
- `WS /ws/metrics` - Real-time metrics stream

## Pages

1. **Overview** (`/`) - Main dashboard with metrics and charts
2. **Sessions** (`/sessions`) - Session explorer
3. **Patterns** (`/patterns`) - Pattern insights
4. **Settings** (`/settings`) - Configuration

