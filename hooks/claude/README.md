# Claude Code Hooks

These hook scripts should be installed in `~/.claude/hooks/telemetry/` to enable telemetry capture from Claude Code.

## Installation

```bash
# Create hooks directory
mkdir -p ~/.claude/hooks/telemetry

# Copy hook scripts
cp hooks/claude/* ~/.claude/hooks/telemetry/

# Make scripts executable
chmod +x ~/.claude/hooks/telemetry/*
```

## Hook Scripts

- `SessionStart` - Session initialization
- `PreToolUse` - Before tool execution
- `PostToolUse` - After tool execution
- `UserPromptSubmit` - User prompt submission
- `Stop` - Session termination
- `PreCompact` - Context window compaction

## Requirements

- Python 3.11+
- Redis running on localhost:6379
- Blueplane Telemetry Core installed (for MessageQueueWriter)

## How It Works

1. Claude Code calls hook script with JSON data via stdin
2. Hook script reads JSON, extracts session_id
3. Builds telemetry event
4. Writes to Redis Streams via MessageQueueWriter
5. Always exits 0 (never blocks Claude Code)

