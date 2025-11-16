# Cursor Database Capture Extension - Implementation Summary

This directory contains an example implementation of how to read trace and log information from Cursor's database and convert it to markdown format. The code has been extracted and de-minified from a production extension.

## Overview

The extension monitors Cursor's SQLite database (`state.vscdb`) for AI conversation traces and automatically converts them to markdown files. It uses a dual monitoring strategy (file watcher + polling) to detect database changes and reads data from Cursor's key-value storage structure.

## Architecture

### Database Structure

Cursor stores data in a non-traditional SQLite format:

```sql
CREATE TABLE ItemTable (key TEXT UNIQUE ON CONFLICT REPLACE, value BLOB);
CREATE TABLE cursorDiskKV (key TEXT UNIQUE ON CONFLICT REPLACE, value BLOB);
```

**Key Points:**

- Data is stored as **key-value pairs**, not traditional SQL tables
- Values are stored as **BLOB/text JSON** that must be parsed
- Common keys include:
  - `aiService.generations` - Array of generation objects
  - `aiService.prompts` - Array of prompt objects
  - Various conversation/composer keys in `cursorDiskKV`

### Database Location

The database is located at:

- **macOS**: `~/Library/Application Support/Cursor/User/workspaceStorage/{workspace-hash}/state.vscdb`
- **Linux**: `~/.config/Cursor/User/workspaceStorage/{workspace-hash}/state.vscdb`
- **Windows**: `~/AppData/Roaming/Cursor/User/workspaceStorage/{workspace-hash}/state.vscdb`

## Implementation Components

### 1. Database Query Methods (`databaseQueries.js`)

#### `DatabaseLoader` Class

**`loadDatabaseTable(dbPath, tableName, keyFilter)`**

- Loads data from `ItemTable` (or specified table)
- Supports filtering by single key or array of keys
- Handles WAL mode automatically
- Returns `Promise<Map<string, any>>`

**`loadCursorConversationData(dbPath, keyPatterns)`**

- Loads conversation data from `cursorDiskKV` table
- Uses LIKE pattern matching for flexible key filtering
- Returns `Promise<Map<string, any>>`

**`loadFromDatabase(dbPath, query, params)`**

- Core database loading method
- Automatically handles WAL mode setup
- Opens database in read-only mode
- Parses JSON values from BLOB storage
- Returns `Promise<Map<string, any>>`

#### `WorkspaceLoader` Class

**`loadCurrentWorkspace()`**

- Finds the current workspace's database
- Matches workspace by file path or folder URI
- Loads all `ItemTable` data for the workspace
- Returns workspace data object with database path and parsed data

### 2. Markdown Generation Methods (`markdownGenerator.js`)

#### Data Normalization

**`normalizeComposer(composerData)`**

- Normalizes composer data from different sources (Cursor/VSCode)
- Routes to appropriate normalization function based on `host` field

**`normalizeCursorComposer(composerData)`**

- Converts Cursor composer format to unified structure
- Extracts capabilities, model config, conversation messages
- Returns: `{ id, name, conversation[], createdAt, lastUpdatedAt }`

**`normalizeVSCodeComposer(sessionData)`**

- Converts VSCode session format to unified structure
- Flattens requests/responses into conversation array
- Returns: `{ id, name, conversation[], createdAt, lastUpdatedAt }`

**`normalizeCursorMessage(message, capabilitiesMap, version, modelName)`**

- Normalizes individual Cursor messages
- Handles timestamps, speaker identification, tool usage
- Processes thinking/reasoning content
- Returns normalized message object

**`normalizeVSCodeRequest(request)`**

- Converts VSCode request/response to conversation messages
- Extracts user message and assistant response
- Handles inline references and confirmations
- Returns array of [userMessage, assistantMessage]

#### Tool Usage Processing

**`adaptToolUse(message, bubbleConversation)`**

- Adapts tool usage data to markdown format
- Routes to tool-specific handlers
- Handles errors and cancellations
- Wraps output in `<tool-use>` tags

**Tool Handlers:**

- `ReadFileToolHandler` - Formats file read operations
- `CodebaseSearchToolHandler` - Formats search results
- `TodoWriteToolHandler` - Formats todo lists with dependencies
- `SearchReplaceToolHandler` - Formats code edits
- `UnknownToolHandler` - Fallback for unknown tools

#### Markdown Generation

**`generateConversationMarkdown(conversation, useUtc)`**

- Generates markdown for a single conversation
- Formats speaker headers with timestamps
- Includes model and agent mode information
- Separates messages with `---` dividers
- Returns markdown string or `null` if empty

**`generateMarkdown(conversations, useUtc, includeComment)`**

- Generates markdown for multiple conversations
- Sorts conversations by creation date
- Adds header comment with version info
- Concatenates individual conversation markdowns
- Returns complete markdown document

#### Utility Functions

**Timestamp Formatting:**

- `formatTimestamp(timestamp, defaultText)` - ISO string format
- `formatTimestampForDisplay(timestamp, defaultText, useUtc)` - Human-readable format
- `formatTimestampLocal(timestamp, defaultText)` - Local timezone, no offset
- `formatTimestampForFilename(timestamp, useUtc)` - Filename-safe format

**Agent Mode:**

- `getAgentModeString(unifiedMode)` - Converts mode number to string ("Ask", "Agent", "Plan", etc.)

## Data Flow

```
1. Database Monitoring
   ├─ File watcher detects state.vscdb changes
   └─ Polling backup (every 30 seconds)

2. Database Reading
   ├─ Open database in read-only mode
   ├─ Check/set WAL mode for concurrent access
   ├─ Query ItemTable for conversation keys
   └─ Parse JSON values from BLOB storage

3. Data Normalization
   ├─ Identify composer type (Cursor/VSCode)
   ├─ Normalize composer structure
   ├─ Normalize individual messages
   └─ Process tool usage data

4. Markdown Generation
   ├─ Format conversation headers
   ├─ Format individual messages
   ├─ Format tool usage sections
   └─ Combine into final markdown

5. File Output
   └─ Write to .specstory/history/ directory
```

## Key Implementation Details

### WAL Mode Handling

The extension automatically handles SQLite WAL (Write-Ahead Logging) mode:

1. Opens database in read-only mode
2. Checks current journal mode
3. If not WAL, temporarily opens in read-write mode to set WAL
4. Reopens in read-only mode for querying

This ensures concurrent access without locking issues.

### Data Version Tracking

The extension tracks `data_version` to detect new entries:

- Queries `MAX(data_version)` from generations
- Compares with last known version
- Processes only new entries between versions

**Note:** This assumes `data_version` exists in the data structure, which may not always be the case.

### Tool Usage Formatting

Tool usage is formatted with:

- Collapsible `<details>` sections
- Tool name and type metadata
- Formatted arguments and results
- Special handling for complex tools (todos, searches, etc.)

### Timestamp Handling

Timestamps are handled in multiple formats:

- Unix milliseconds (from Cursor)
- Duration offsets (for relative timing)
- ISO strings (for display)
- Filename-safe formats (for file naming)

## Usage Examples

### Example 1: Loading AI Service Data from ItemTable

```javascript
const { DatabaseLoader } = require("./databaseQueries");

// Load specific keys from ItemTable
const dbPath =
  "/Users/username/Library/Application Support/Cursor/User/workspaceStorage/66b4e47d8cd79622d5b1b18f44882398/state.vscdb";

// Example: Load aiService.generations (single key)
const generationsData = await DatabaseLoader.loadDatabaseTable(
  dbPath,
  "ItemTable", // tableName - always "ItemTable" for Cursor
  "aiService.generations" // keyFilter - single key string
);

// Example: Load multiple AI service keys (array of keys)
const aiServiceData = await DatabaseLoader.loadDatabaseTable(
  dbPath,
  "ItemTable",
  ["aiService.generations", "aiService.prompts"] // keyFilter - array of keys
);

// Example: Load all composer-related data
const composerData = await DatabaseLoader.loadDatabaseTable(
  dbPath,
  "ItemTable",
  [
    "composer.composerData",
    "workbench.backgroundComposer.workspacePersistentData",
  ]
);

// Access the data (values are parsed JSON)
const generations = aiServiceData.get("aiService.generations");
// generations is a JSON array: [{ unixMs: 1762046253035, generationUUID: "...", type: "cmdk", ... }]

const prompts = aiServiceData.get("aiService.prompts");
// prompts is a JSON array: [{ text: "...", commandType: 4 }]
```

### Example 2: Loading Conversation Data from cursorDiskKV

```javascript
// Example: Load conversation data with pattern matching
const conversationData = await DatabaseLoader.loadCursorConversationData(
  dbPath,
  ["composer", "session", "chat"] // keyPatterns - LIKE patterns for matching keys
);

// This queries: SELECT * FROM cursorDiskKV WHERE value IS NOT NULL
//   AND (key LIKE '%composer%' OR key LIKE '%session%' OR key LIKE '%chat%')
```

### Example 3: Real Composer Data Structure

```javascript
// Example composerData from ItemTable key "composer.composerData"
const composerData = {
  host: "cursor", // or "vscode"
  composerId: "a444abdd-2743-4711-b38f-207c8c7427dc",
  name: "Untitled", // or user-provided name
  createdAt: 1762033584314, // Unix timestamp in milliseconds
  lastUpdatedAt: 1762033584314,
  _v: 3, // version number

  // Capabilities array - contains tool usage metadata
  capabilities: [
    {
      type: 15, // capabilityType - 15 = tool usage
      data: {
        bubbleDataMap: JSON.stringify({
          "bubble-id-1": {
            /* tool usage data */
          },
          "bubble-id-2": {
            /* tool usage data */
          },
        }),
      },
    },
    {
      type: 1, // other capability types
      data: {
        /* ... */
      },
    },
  ],

  // Model configuration
  modelConfig: {
    modelName: "claude-3-5-sonnet-20241022",
  },

  // Conversation messages array
  conversation: [
    {
      bubbleId: "msg-1",
      type: 1, // 1 = user, 2 = assistant
      text: "How do I implement authentication?",
      timingInfo: {
        clientStartTime: 1762033584314,
        clientRpcSendTime: 1762033584400,
        clientSettleTime: 1762033585000,
        clientEndTime: 1762033585100,
      },
      capabilityType: 0, // 0 = regular message, 15 = tool usage
      unifiedMode: 2, // 1 = Ask, 2 = Agent, 5 = Plan
      modelInfo: {
        modelName: "claude-3-5-sonnet-20241022",
      },
      thinking: {
        // Optional reasoning content
        text: "The user wants to implement authentication...",
      },
      toolFormerData: {
        // Tool usage data (if capabilityType === 15)
        name: "read_file",
        rawArgs: JSON.stringify({ target_file: "auth.js" }),
        result: JSON.stringify({
          /* file contents */
        }),
        status: "success",
      },
    },
    {
      bubbleId: "msg-2",
      type: 2, // assistant response
      text: "Here's how to implement authentication...",
      // ... similar structure
    },
  ],
};
```

### Example 4: Real Session Data Structure (VSCode)

```javascript
// Example sessionData from VSCode format
const sessionData = {
  host: "vscode",
  sessionId: "session-abc-123",
  name: "GitHub Copilot Chat",
  creationDate: 1762033584314,
  lastMessageDate: 1762033585000,

  requests: [
    {
      requestId: "req-1",
      responseId: "resp-1",
      timestamp: 1762033584314,
      message: {
        text: "How do I implement authentication?",
      },
      response: [
        {
          value: "Here's how to implement authentication...",
        },
        {
          kind: "inlineReference",
          inlineReference: {
            path: "/path/to/auth.js",
            name: "auth.js",
          },
        },
      ],
      modelId: "gpt-4",
      result: {
        timings: {
          firstProgress: 100,
          totalElapsed: 2000,
        },
      },
    },
  ],
};
```

### Example 5: Capabilities Map Structure

```javascript
// Example capabilitiesMap built from composerData.capabilities
const capabilitiesMap = new Map();

// After processing composerData.capabilities:
capabilitiesMap.set(15, {
  // key = capabilityType (15 = tool usage)
  bubbleDataMap: {
    // parsed from JSON string
    "bubble-id-1": {
      name: "read_file",
      tool: 1, // tool type identifier
      rawArgs: JSON.stringify({ target_file: "auth.js" }),
      result: JSON.stringify({
        /* file contents */
      }),
      status: "success",
      error: null,
    },
    "bubble-id-2": {
      name: "codebase_search",
      tool: 2,
      rawArgs: JSON.stringify({ query: "authentication" }),
      result: JSON.stringify([{ path: "auth.js", content: "..." }]),
      status: "success",
    },
  },
});

capabilitiesMap.set(1, {
  // Other capability type data
});
```

### Example 6: Complete Workflow

```javascript
const { DatabaseLoader, WorkspaceLoader } = require('./databaseQueries');
const { generateMarkdown, normalizeComposer } = require('./markdownGenerator');
const fs = require('fs').promises;
const path = require('path');

async function captureConversation() {
  // 1. Find workspace database
  const workspaceLoader = new WorkspaceLoader(pathsService, context);
  const workspace = await workspaceLoader.loadCurrentWorkspace();

  if (!workspace) {
    console.error("No workspace found");
    return;
  }

  // 2. Load composer data from ItemTable
  // Real keys used in extension.js:
  const itemTableData = await DatabaseLoader.loadDatabaseTable(
    workspace.dbPath,
    "ItemTable",  // Always "ItemTable" for Cursor
    "composer.composerData"  // Actual key from Cursor database
  );

  // 3. Extract and parse composer data
  const composerDataJson = itemTableData.get("composer.composerData");
  // composerDataJson structure:
  // {
  //   allComposers: [{ composerId, createdAt, unifiedMode, ... }],
  //   selectedComposerIds: [...],
  //   lastFocusedComposerIds: [...]
  // }

  // For each composer, you'd need to load its full data
  // (The extension.js does this differently - it loads from a different source)

  // 4. Normalize composer data
  const normalized = normalizeComposer({
    host: "cursor",
    composerId: "a444abdd-2743-4711-b38f-207c8c7427dc",
    name: "Untitled",
    capabilities: [...],
    conversation: [...],
    // ... full composer data structure
  });

  // 5. Generate markdown
  const markdown = generateMarkdown([normalized], true, true);

  // 6. Write to file
  const outputPath = path.join(
    workspace.folder,
    ".specstory",
    "history",
    `${normalized.id}.md`
  );
  await fs.writeFile(outputPath, markdown, "utf8");
}
```

### Example 7: Actual Key Patterns Used

Based on the extension.js and database audit, here are real examples:

```javascript
// Trace-relevant keys from ItemTable (from CURSOR_DISK_KV_AUDIT.md)
const TRACE_RELEVANT_KEYS = [
  "aiService.generations", // AI generation traces
  "aiService.prompts", // User prompts
  "composer.composerData", // Composer sessions
  "workbench.backgroundComposer.workspacePersistentData", // Background composer
  "workbench.agentMode.exitInfo", // Agent mode state
  "interactive.sessions", // Interactive sessions
  "history.entries", // File open history
  "cursorAuth/workspaceOpenedDate", // Workspace lifecycle
];

// Load all trace-relevant data
const traceData = await DatabaseLoader.loadDatabaseTable(
  dbPath,
  "ItemTable",
  TRACE_RELEVANT_KEYS // Array of keys
);

// Pattern matching for cursorDiskKV (currently empty, but for future use)
const conversationPatterns = [
  "composer%", // Matches keys starting with "composer"
  "%session%", // Matches keys containing "session"
  "%chat%", // Matches keys containing "chat"
];

const conversationData = await DatabaseLoader.loadCursorConversationData(
  dbPath,
  conversationPatterns
);
```

## Actual Data Structures from Cursor Database

### aiService.generations (from ItemTable)

**Key**: `"aiService.generations"`  
**Value Type**: JSON array (stored as BLOB)

```json
[
  {
    "unixMs": 1762046253035,
    "generationUUID": "dd4317f0-22e0-4153-8f11-9b5aa5fc7946",
    "type": "cmdk",
    "textDescription": "User asked about implementing authentication"
  },
  {
    "unixMs": 1762046254000,
    "generationUUID": "ee5428g1-33f1-5264-9c22-ac6bb6gd8057",
    "type": "cmdk",
    "textDescription": "AI provided code example for authentication"
  }
]
```

**Note**: This is stored as a **key-value pair** in `ItemTable`, NOT as a SQL table.

### aiService.prompts (from ItemTable)

**Key**: `"aiService.prompts"`  
**Value Type**: JSON array (stored as BLOB)

```json
[
  {
    "text": "how could i use cursor hooks to capture meaningful telemetry...",
    "commandType": 4
  },
  {
    "text": "implement authentication with JWT",
    "commandType": 4
  }
]
```

### composer.composerData (from ItemTable)

**Key**: `"composer.composerData"`  
**Value Type**: JSON object (stored as BLOB)

```json
{
  "allComposers": [
    {
      "type": "head",
      "composerId": "a444abdd-2743-4711-b38f-207c8c7427dc",
      "createdAt": 1762033584314,
      "unifiedMode": "agent",
      "forceMode": "edit",
      "hasUnreadMessages": false,
      "totalLinesAdded": 0,
      "totalLinesRemoved": 0,
      "isArchived": false,
      "isWorktree": false,
      "isSpec": false
    }
  ],
  "selectedComposerIds": ["a444abdd-2743-4711-b38f-207c8c7427dc"],
  "lastFocusedComposerIds": ["a444abdd-2743-4711-b38f-207c8c7427dc"]
}
```

### Actual Database Query Examples

```javascript
// Example 1: Query ItemTable for specific key
const query1 = `SELECT * FROM ItemTable WHERE key = 'aiService.generations'`;
// Returns: { key: "aiService.generations", value: BLOB containing JSON array }

// Example 2: Query ItemTable for multiple keys
const query2 = `SELECT * FROM ItemTable WHERE key IN ('aiService.generations', 'aiService.prompts')`;
// Returns: Array of { key, value } pairs

// Example 3: Query cursorDiskKV with pattern matching
const query3 = `SELECT * FROM cursorDiskKV WHERE value IS NOT NULL AND (key LIKE '%composer%' OR key LIKE '%session%')`;
// Returns: Array of matching key-value pairs

// Example 4: Check journal mode (for WAL handling)
const query4 = `PRAGMA journal_mode;`;
// Returns: { journal_mode: "WAL" } or { journal_mode: "delete" }
```

### Parameter Examples Summary

| Parameter     | Type     | Example Values                                   | Notes                                |
| ------------- | -------- | ------------------------------------------------ | ------------------------------------ |
| `tableName`   | string   | `"ItemTable"`                                    | Always `"ItemTable"` for Cursor data |
| `keyFilter`   | string   | `"aiService.generations"`                        | Single key                           |
| `keyFilter`   | string[] | `["aiService.generations", "aiService.prompts"]` | Multiple keys                        |
| `keyPatterns` | string[] | `["composer%", "%session%"]`                     | LIKE patterns for cursorDiskKV       |

## Dependencies

- `@vscode/sqlite3` - SQLite database access
- `vscode` - VSCode extension API
- `fs` - File system operations
- `path` - Path manipulation

## Limitations & Notes

1. **Schema Mismatch**: The code may expect SQL tables, but Cursor uses `ItemTable` key-value pairs. Some queries may need adjustment.

2. **Data Version**: The `data_version` field may not exist in all data structures. Version tracking may need alternative methods.

3. **Auto-save Delay**: Auto-save only works when Cursor flushes SQLite data to disk, resulting in a small delay after AI responses.

4. **WAL Mode**: The extension sets the database to WAL mode for concurrent read access, which requires temporary write access.

5. **Tool Handler Mapping**: The tool handler mapping is simplified. Production implementations may have more comprehensive tool handlers.

## File Structure

```
example_cursor_capture/
├── extension.js              # Original minified extension (reference)
├── databaseQueries.js        # Database reading methods
├── markdownGenerator.js      # Markdown generation methods
└── README.md                 # This file
```

## References

- Cursor Database Schema Investigation: `docs/CURSOR_SCHEMA_INVESTIGATION.md`
- Cursor Disk KV Audit: `docs/CURSOR_DISK_KV_AUDIT.md`
- Database Architecture: `docs/architecture/layer2_db_architecture.md`
