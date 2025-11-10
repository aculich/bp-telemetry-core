# Cursor Telemetry Capture

This directory contains the Cursor platform implementation for Blueplane Telemetry Core.

## Components

### Hooks (`hooks/`)

Python scripts that capture telemetry events from Cursor IDE:

1. **before_submit_prompt.py** - User prompt submission
2. **after_agent_response.py** - AI response completion
3. **before_mcp_execution.py** - Before MCP tool execution
4. **after_mcp_execution.py** - After MCP tool execution
5. **after_file_edit.py** - File modifications
6. **before_shell_execution.py** - Before shell command
7. **after_shell_execution.py** - After shell command
8. **before_read_file.py** - Before file read
9. **stop.py** - Session termination

### Extension (`extension/`)

TypeScript VSCode extension that manages:
- Session ID generation and environment variables
- Database monitoring (Cursor's SQLite database)
- Message queue integration

### Configuration

- **hooks.json** - Cursor hooks configuration file
- **hook_base.py** - Shared utilities for all hooks

## Installation

### Prerequisites

- Cursor IDE installed
- Python 3.11+
- Redis server running (localhost:6379)

### Setup

1. **Copy hooks to your project:**
   ```bash
   cp -r hooks/ .cursor/hooks/telemetry/
   cp hooks.json .cursor/hooks.json
   ```

2. **Install Python dependencies:**
   ```bash
   pip install redis pyyaml
   ```

3. **Start Redis server:**
   ```bash
   redis-server
   ```

4. **Configure Redis streams:**
   ```bash
   redis-cli XGROUP CREATE telemetry:events processors $ MKSTREAM
   redis-cli XGROUP CREATE cdc:events workers $ MKSTREAM
   ```

### Extension Installation (Optional)

For database monitoring and automatic session management:

1. Build the extension:
   ```bash
   cd extension
   npm install
   npm run compile
   ```

2. Install in Cursor:
   - Open Cursor
   - Go to Extensions
   - Click "Install from VSIX"
   - Select the compiled `.vsix` file

## Usage

Once installed, hooks will automatically capture events as you work in Cursor:

- ✅ Prompts and responses are logged
- ✅ Tool executions are tracked
- ✅ File edits are recorded
- ✅ Shell commands are monitored
- ✅ Session lifecycle is captured

All data goes to Redis Streams (`telemetry:events`) for processing by Layer 2.

## Environment Variables

Hooks require these environment variables (set by extension):

- `CURSOR_SESSION_ID` - Current session identifier
- `CURSOR_WORKSPACE_HASH` - Hashed workspace path

## Privacy

Hooks follow strict privacy guidelines:

- ❌ No code content captured
- ❌ No file paths stored (only extensions)
- ❌ No prompt text content
- ✅ Only metadata and metrics

See `config/privacy.yaml` for full privacy settings.

## Troubleshooting

### Hooks not firing

1. Check hooks.json is in `.cursor/` directory
2. Verify hooks are executable: `chmod +x hooks/*.py`
3. Check Redis is running: `redis-cli PING`

### Events not appearing in queue

1. Check Redis connection: `redis-cli XLEN telemetry:events`
2. View hook logs: `.cursor/hooks.log`
3. Test hook manually:
   ```bash
   export CURSOR_SESSION_ID=test-session
   python hooks/before_submit_prompt.py --workspace-root /tmp --generation-id test-123 --prompt-length 100
   ```

### Redis connection errors

1. Ensure Redis is running: `redis-server`
2. Check port 6379 is open
3. Verify config: `config/redis.yaml`

## Development

### Testing Hooks

Test individual hooks:

```bash
export CURSOR_SESSION_ID=test-session-123
export CURSOR_WORKSPACE_HASH=abc123def456

python hooks/before_submit_prompt.py \
  --workspace-root /path/to/workspace \
  --generation-id gen-456 \
  --prompt-length 150
```

Check Redis queue:

```bash
redis-cli XLEN telemetry:events
redis-cli XREAD COUNT 1 STREAMS telemetry:events 0-0
```

### Adding New Hooks

1. Create new hook script in `hooks/`
2. Extend `CursorHookBase` class
3. Implement `execute()` method
4. Add to `hooks.json` configuration
5. Make executable: `chmod +x hooks/your_hook.py`

## Architecture

See main documentation:
- [Layer 1 Capture](../../../docs/architecture/layer1_capture.md)
- [Database Architecture](../../../docs/architecture/layer2_db_architecture.md)
- [Overall Architecture](../../../docs/ARCHITECTURE.md)
