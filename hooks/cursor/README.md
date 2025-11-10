# Cursor Hooks

These hook scripts should be installed in `.cursor/hooks/telemetry/` (project-level) to enable telemetry capture from Cursor.

## Installation

```bash
# Create hooks directory in your project
mkdir -p .cursor/hooks/telemetry

# Copy hook scripts
cp hooks/cursor/* .cursor/hooks/telemetry/

# Make scripts executable
chmod +x .cursor/hooks/telemetry/*
```

## Hook Scripts

- `beforeSubmitPrompt` - Before user prompt submission
- `afterAgentResponse` - After AI response
- `beforeMCPExecution` - Before MCP tool execution
- `afterMCPExecution` - After MCP tool execution
- `afterFileEdit` - After file modification
- `beforeShellExecution` - Before shell command
- `afterShellExecution` - After shell command
- `beforeReadFile` - Before file read
- `stop` - Session termination

## Requirements

- Python 3.11+
- Redis running on localhost:6379
- Blueplane Telemetry Core installed (for MessageQueueWriter)
- Cursor extension (for session management and database monitoring)

## How It Works

1. Cursor extension sets `CURSOR_SESSION_ID` environment variable
2. Cursor calls hook script with command-line arguments
3. Hook script reads session_id from environment
4. Builds telemetry event from arguments
5. Writes to Redis Streams via MessageQueueWriter
6. Always exits 0 (never blocks Cursor)

## Note

The Cursor extension (TypeScript) is required for:
- Session management (setting CURSOR_SESSION_ID)
- Database monitoring (watching Cursor's SQLite database)

The hooks can work standalone if you manually set `CURSOR_SESSION_ID`, but full functionality requires the extension.

