/**
 * Markdown Generation Methods for Cursor Extension
 *
 * Extracted and de-minified from example_cursor_capture/extension.js
 *
 * These methods transform database trace/log data into markdown format.
 */

const MARKDOWN_VERSION = "2.0.0";

/**
 * Format timestamp to ISO string
 */
function formatTimestamp(timestamp, defaultText = "Invalid Date") {
  try {
    if (timestamp === null) {
      return defaultText;
    }
    timestamp = Number(timestamp);
    const date = new Date(timestamp);
    return isNaN(date.getTime())
      ? defaultText
      : date.toISOString() ?? defaultText;
  } catch {
    return defaultText;
  }
}

/**
 * Format date components for display
 */
function formatDateComponents(date, useUtc = false) {
  const yearString = String(
    useUtc ? date.getUTCFullYear() : date.getFullYear()
  );
  const monthsString = String(
    (useUtc ? date.getUTCMonth() : date.getMonth()) + 1
  ).padStart(2, "0");
  const dayString = String(
    useUtc ? date.getUTCDate() : date.getDate()
  ).padStart(2, "0");
  const hourString = String(
    useUtc ? date.getUTCHours() : date.getHours()
  ).padStart(2, "0");
  const minuteString = String(
    useUtc ? date.getUTCMinutes() : date.getMinutes()
  ).padStart(2, "0");

  const timezoneOffset = useUtc ? 0 : date.getTimezoneOffset();
  let offsetString = "Z";

  if (timezoneOffset !== 0) {
    const hours = Math.floor(Math.abs(timezoneOffset) / 60);
    const minutes = Math.abs(timezoneOffset) % 60;
    const sign = timezoneOffset > 0 ? "-" : "+";
    const hoursStr = hours.toString().padStart(2, "0");
    const minutesStr = minutes.toString().padStart(2, "0");
    offsetString = `${sign}${hoursStr}${minutesStr}`;
  }

  return {
    yearString,
    monthsString,
    dayString,
    hourString,
    minuteString,
    offsetString,
  };
}

/**
 * Format timestamp to filename-safe format
 */
function formatTimestampForFilename(timestamp, useUtc = false) {
  const date = new Date(timestamp);
  const components = formatDateComponents(date, useUtc);
  return `${components.yearString}-${components.monthsString}-${components.dayString}_${components.hourString}-${components.minuteString}${components.offsetString}`;
}

/**
 * Format timestamp for display
 */
function formatTimestampForDisplay(
  timestamp,
  defaultText = "Invalid Date",
  useUtc = false
) {
  try {
    if (timestamp === null) {
      return defaultText;
    }

    let date;
    if (timestamp instanceof Date) {
      date = timestamp;
    } else {
      date = new Date(timestamp);
    }

    if (isNaN(date.getTime())) {
      return defaultText;
    }

    const components = formatDateComponents(date, useUtc);
    return `${components.yearString}-${components.monthsString}-${components.dayString} ${components.hourString}:${components.minuteString}${components.offsetString}`;
  } catch {
    return defaultText;
  }
}

/**
 * Format timestamp for display (local timezone, no offset suffix)
 */
function formatTimestampLocal(timestamp, defaultText = "Invalid Date") {
  const formatted = formatTimestampForDisplay(timestamp, defaultText, false);
  return formatted === defaultText
    ? formatted
    : formatted.replace(/[+-]\d{4}$|Z$/, "").trim();
}

/**
 * Get agent mode string from unified mode number
 */
function getAgentModeString(unifiedMode) {
  switch (unifiedMode) {
    case 1:
      return "Ask";
    case 2:
      return "Agent";
    case 5:
      return "Plan";
    default:
      return unifiedMode ? "Custom" : "";
  }
}

/**
 * Normalize Cursor composer data to unified format
 */
function normalizeCursorComposer(composerData) {
  const capabilitiesMap = new Map();

  // Build capabilities map
  for (const capability of composerData.capabilities || []) {
    const capabilityData = { ...capability.data };
    if (capabilityData.bubbleDataMap) {
      capabilityData.bubbleDataMap = JSON.parse(capabilityData.bubbleDataMap);
    }
    capabilitiesMap.set(capability.type, capabilityData);
  }

  // Extract model name
  const modelName =
    composerData.modelConfig &&
    typeof composerData.modelConfig === "object" &&
    "modelName" in composerData.modelConfig
      ? composerData.modelConfig.modelName
      : undefined;

  return {
    id: composerData.composerId,
    name: composerData.name ?? "Untitled",
    conversation: (composerData.conversation || []).map((msg) =>
      normalizeCursorMessage(msg, capabilitiesMap, composerData._v, modelName)
    ),
    createdAt: composerData.createdAt,
    lastUpdatedAt: composerData.lastUpdatedAt ?? composerData.createdAt,
  };
}

/**
 * Normalize VSCode composer data to unified format
 */
function normalizeVSCodeComposer(sessionData) {
  return {
    id: sessionData.sessionId,
    name: sessionData.name ?? "Untitled",
    conversation: sessionData.requests.flatMap((request) =>
      normalizeVSCodeRequest(request)
    ),
    createdAt: sessionData.creationDate,
    lastUpdatedAt: sessionData.lastMessageDate,
  };
}

/**
 * Normalize composer data based on host type
 */
function normalizeComposer(composerData) {
  switch (composerData.host) {
    case "cursor":
      return normalizeCursorComposer(composerData);
    case "vscode":
      return normalizeVSCodeComposer(composerData);
    default:
      throw new Error(`Unknown composer host: ${JSON.stringify(composerData)}`);
  }
}

/**
 * Normalize Cursor message to unified format
 */
function normalizeCursorMessage(message, capabilitiesMap, version, modelName) {
  let timestamp = message.timingInfo?.clientStartTime;

  // Handle timestamp conversion if it's a duration (less than epoch)
  if (timestamp && typeof timestamp === "number" && timestamp < 946684800000) {
    const endTime =
      message.timingInfo?.clientRpcSendTime ||
      message.timingInfo?.clientSettleTime ||
      message.timingInfo?.clientEndTime;
    if (endTime && typeof endTime === "number") {
      timestamp = Math.floor(endTime - timestamp);
    }
  }

  const normalizedMessage = {
    messageId: message.bubbleId,
    speaker: message.type === 1 ? "user" : "assistant",
    text: message.thinking?.text
      ? `<think><details><summary>Thought Process</summary>\n${message.thinking.text}</details></think>`
      : message.text,
    timestamp: timestamp,
    type: message.capabilityType,
    modelName: message?.modelInfo?.modelName ?? modelName ?? "",
    agentMode: getAgentModeString(message?.unifiedMode),
  };

  // Handle tool usage (capabilityType 15)
  if (message.capabilityType && message.capabilityType === 15) {
    const capabilityData = capabilitiesMap.get(message.capabilityType);
    if (capabilityData?.bubbleDataMap) {
      try {
        let bubbleData;
        if (version && version >= 3) {
          bubbleData = message.toolFormerData;
        } else {
          bubbleData = capabilityData.bubbleDataMap[message.bubbleId];
        }

        if (bubbleData) {
          adaptToolUse(normalizedMessage, bubbleData);
        }
      } catch (err) {
        console.warn("Failed to parse capability data:", err);
      }
    }
  }

  return normalizedMessage;
}

/**
 * Normalize VSCode request to conversation messages
 */
function normalizeVSCodeRequest(request) {
  const userMessage = {
    role: "user",
    content: "",
  };
  const assistantMessage = {
    role: "assistant",
    content: "",
  };

  userMessage.content = request.message.text;

  for (const response of request.response) {
    if (response.value) {
      assistantMessage.content += response.value;
    } else if (response.kind === "confirmation") {
      assistantMessage.content += response.message;
    } else if (response.kind === "inlineReference") {
      const path = response.inlineReference.path;
      const name = response.inlineReference.name ?? path?.split("/")?.pop();
      assistantMessage.content += `\`${name}\``;
    }
  }

  const userMsg = {
    messageId: request.requestId,
    speaker: "user",
    text: userMessage?.content ?? "",
    timestamp: request.timestamp,
    type: 0,
  };

  const assistantMsg = {
    messageId: request.responseId,
    speaker: "assistant",
    text: assistantMessage?.content ?? "",
    modelName: request.modelId ?? "",
    agentMode: "",
    timestamp:
      request.timestamp +
      (request.result?.timings?.firstProgress ?? 0) +
      (request.result?.timings?.totalElapsed ?? 0),
    type: 0,
  };

  return [userMsg, assistantMsg];
}

/**
 * Adapt tool use message with tool-specific formatting
 */
function adaptToolUse(message, bubbleConversation) {
  if (bubbleConversation.tool === 0) {
    handleToolError(message, bubbleConversation);
    return message;
  }

  const toolInfo = getToolHandler(bubbleConversation);
  const toolType = toolInfo?.[0];
  const ToolHandler = toolInfo?.[1];

  if (!ToolHandler) {
    console.error(
      `Unknown bubble conversation handler: ${bubbleConversation.name}`
    );
    console.error(bubbleConversation);
    // Use unknown handler
    const unknownHandler = new UnknownToolHandler(bubbleConversation);
    unknownHandler.adaptMessage(message);
    return message;
  }

  const handler = new ToolHandler(bubbleConversation);

  if (bubbleConversation.status === "error") {
    handleToolError(message, bubbleConversation);
  } else if (bubbleConversation.status === "cancelled") {
    message.text = "Cancelled";
  } else {
    try {
      handler.adaptMessage(message);
    } catch (err) {
      console.error("Error adapting bubble conversation data:", err);
      console.error(bubbleConversation);
      const unknownHandler = new UnknownToolHandler(bubbleConversation);
      unknownHandler.adaptMessage(message);
    }

    message.text = `<tool-use data-tool-type="${toolType}" data-tool-name="${
      bubbleConversation.name
    }">\n${message?.text || ""}\n</tool-use>`;
  }

  // Clean up text
  if (message.thinking?.text) {
    message.thinking.text = message.thinking.text.trim();
  }
  message.text = message.text.trim();

  return message;
}

/**
 * Handle tool error
 */
function handleToolError(message, bubbleConversation) {
  if (bubbleConversation.error) {
    try {
      const errorData = JSON.parse(bubbleConversation.error);
      message.text = errorData.clientVisibleErrorMessage;
    } catch {
      message.text = "An unknown error occurred";
    }
  } else {
    message.text = "An unknown error occurred";
  }
}

/**
 * Base tool handler class
 */
class BaseToolHandler {
  constructor(bubbleConversation) {
    this.bubbleConversation = bubbleConversation;
  }

  adaptMessage(message) {
    message.text = `<details><summary>Tool use: **${this.bubbleConversation.name}**</summary>\n\nTool execution details\n\n</details>`;
  }
}

/**
 * Unknown tool handler
 */
class UnknownToolHandler extends BaseToolHandler {
  adaptMessage(message) {
    message.text = `<details><summary>Tool use: **${this.bubbleConversation.name}** • Unknown tool</summary>\n\nUnknown tool type\n\n</details>`;
  }
}

/**
 * Read file tool handler
 */
class ReadFileToolHandler extends BaseToolHandler {
  adaptMessage(message) {
    try {
      const args = JSON.parse(this.bubbleConversation.rawArgs);
      const result = JSON.parse(this.bubbleConversation.result);

      let markdown = `<details><summary>Tool use: **read_file**</summary>\n\n`;
      markdown += `**File:** \`${args.target_file}\`\n\n`;

      if (result) {
        markdown += `\`\`\`\n${result}\n\`\`\`\n\n`;
      }

      markdown += `</details>`;
      message.text = markdown;
    } catch (err) {
      message.text = `<details><summary>Tool use: **read_file** • Error parsing tool data</summary>\n\nError: ${err.message}\n\n</details>`;
    }
  }
}

/**
 * Codebase search tool handler
 */
class CodebaseSearchToolHandler extends BaseToolHandler {
  adaptMessage(message) {
    try {
      const args = JSON.parse(this.bubbleConversation.rawArgs);
      const result = JSON.parse(this.bubbleConversation.result);

      let markdown = `<details><summary>Tool use: **codebase_search**</summary>\n\n`;
      markdown += `**Query:** ${args.query}\n\n`;

      if (result && result.length > 0) {
        markdown += `**Results:**\n\n`;
        result.forEach((item, idx) => {
          markdown += `${idx + 1}. ${item.path || item.file || "Unknown"}\n`;
        });
      }

      markdown += `\n</details>`;
      message.text = markdown;
    } catch (err) {
      message.text = `<details><summary>Tool use: **codebase_search** • Error parsing tool data</summary>\n\nError: ${err.message}\n\n</details>`;
    }
  }
}

/**
 * Todo write tool handler
 */
class TodoWriteToolHandler extends BaseToolHandler {
  adaptMessage(message) {
    try {
      const todos = JSON.parse(this.bubbleConversation.result);
      const markdown = this.createTodoMarkdown(todos.finalTodos);
      message.text = markdown;
    } catch (err) {
      message.text = `<details><summary>Tool use: **todo_write** • Error parsing todo list data</summary>\n\nError: ${err.message}\n\n</details>`;
    }
  }

  createTodoMarkdown(todos) {
    const sortedTodos = this.topologicalSort(todos);
    let markdown = `<details><summary>Tool use: **todo_write** • Todo List</summary>\n\n`;

    sortedTodos.forEach((todo) => {
      const checkbox = this.getCheckboxState(todo.status);
      markdown += `- [${checkbox}] ${todo.content}\n`;
      if (todo.dependencies && todo.dependencies.length > 0) {
        markdown += `  - Dependencies: ${todo.dependencies.join(", ")}\n`;
      }
    });

    markdown += `\n</details>`;
    return markdown;
  }

  topologicalSort(todos) {
    const todoMap = new Map();
    const visited = new Set();
    const visiting = new Set();
    const result = [];

    todos.forEach((todo) => {
      todoMap.set(todo.id, todo);
    });

    const visit = (todoId) => {
      if (visited.has(todoId) || visiting.has(todoId)) {
        return;
      }

      const todo = todoMap.get(todoId);
      if (todo) {
        visiting.add(todoId);

        if (todo.dependencies) {
          todo.dependencies.forEach((depId) => {
            visit(depId);
          });
        }

        visiting.delete(todoId);
        visited.add(todoId);
        result.push(todo);
      }
    };

    todos.forEach((todo) => {
      visit(todo.id);
    });

    return result;
  }

  getCheckboxState(status) {
    switch (status) {
      case "cancelled":
        return "!";
      case "in_progress":
        return "-";
      case "completed":
        return "x";
      case "pending":
      default:
        return " ";
    }
  }
}

/**
 * Search replace tool handler
 */
class SearchReplaceToolHandler extends BaseToolHandler {
  adaptMessage(message) {
    try {
      const args = JSON.parse(this.bubbleConversation.rawArgs);
      const result = JSON.parse(this.bubbleConversation.result);

      let markdown = `<details><summary>Tool use: **search_replace**</summary>\n\n`;
      markdown += `**File:** \`${args.file_path}\`\n\n`;

      if (args.old_string) {
        markdown += `**Old:**\n\`\`\`\n${args.old_string}\n\`\`\`\n\n`;
      }

      if (args.new_string) {
        markdown += `**New:**\n\`\`\`\n${args.new_string}\n\`\`\`\n\n`;
      }

      markdown += `</details>`;
      message.text = markdown;
    } catch (err) {
      message.text = `<details><summary>Tool use: **search_replace** • Error parsing tool data</summary>\n\nError: ${err.message}\n\n</details>`;
    }
  }
}

/**
 * Get tool handler class based on tool name
 * Returns [toolType, HandlerClass]
 *
 * Must be defined after all tool handler classes are declared.
 */
function getToolHandler(bubbleConversation) {
  // Tool handler registry - maps tool names to handler classes
  const toolHandlers = {
    read_file: ["read_file", ReadFileToolHandler],
    codebase_search: ["codebase_search", CodebaseSearchToolHandler],
    todo_write: ["todo_write", TodoWriteToolHandler],
    search_replace: ["search_replace", SearchReplaceToolHandler],
    // Add more tool handlers as needed
  };

  return toolHandlers[bubbleConversation.name] || null;
}

/**
 * Generate markdown for a single conversation
 */
function generateConversationMarkdown(conversation, useUtc = false) {
  let markdown = "";
  let lastSpeaker = "";
  let lastAgentMode = null;

  if (!conversation.conversation || conversation.conversation.length === 0) {
    return null;
  }

  const createdAtFormatted = formatTimestampForDisplay(
    conversation.createdAt,
    undefined,
    useUtc
  );
  markdown += `# ${
    conversation.name ?? "Untitled"
  } (${createdAtFormatted})\n\n`;

  for (let i = 0; i < conversation.conversation.length; i++) {
    const message = conversation.conversation[i];
    const isUser = message.speaker === "user";
    let speakerLabel = isUser ? "User" : "Agent";
    let messageBlock = "";

    // Add speaker header when speaker changes
    if (message.speaker !== lastSpeaker) {
      if (isUser) {
        // For user messages, try to find the next assistant timestamp
        let userLabel = speakerLabel;
        for (let j = i; j < conversation.conversation.length; j++) {
          const nextMsg = conversation.conversation[j + 1];
          if (nextMsg && nextMsg.speaker === "assistant" && nextMsg.timestamp) {
            const timestampFormatted = formatTimestampForDisplay(
              nextMsg.timestamp,
              undefined,
              useUtc
            );
            userLabel = `${speakerLabel} (${timestampFormatted})`;
            break;
          }
        }
        speakerLabel = userLabel;
      } else {
        // For assistant messages, add model and mode info
        let modeInfo = "";
        if (lastAgentMode) {
          modeInfo = `mode ${lastAgentMode}`;
        } else if (message.agentMode) {
          modeInfo = `mode ${message.agentMode}`;
        }

        const modelInfo = message.modelName ? `model ${message.modelName}` : "";
        const infoParts = [modelInfo, modeInfo].filter(Boolean).join(", ");

        if (infoParts) {
          speakerLabel += ` (${infoParts})`;
        }
      }

      messageBlock += `_**${speakerLabel}**_\n\n`;
    }

    messageBlock += `${message.text}\n\n---\n\n`;
    markdown += messageBlock;

    lastSpeaker = message.speaker;
    lastAgentMode = message.agentMode;
  }

  return markdown;
}

/**
 * Sort conversations by creation timestamp
 */
function sortConversationsByDate(conversations) {
  return [...conversations].sort((a, b) => a.createdAt - b.createdAt);
}

/**
 * Generate markdown for multiple conversations
 */
function generateMarkdown(conversations, useUtc = true, includeComment = true) {
  let markdown = `<!-- Generated by SpecStory, Markdown v${MARKDOWN_VERSION} -->\n\n`;

  if (includeComment) {
    markdown += `<!-- `;
    const sessionIds = conversations.map((c) => c.id);
    if (sessionIds.length > 0) {
      markdown += `Session${sessionIds.length > 1 ? "s" : ""} ${sessionIds.join(
        ", "
      )}`;
    }

    if (conversations.length === 1 && conversations[0]?.createdAt) {
      markdown += ` (${formatTimestampForDisplay(
        conversations[0].createdAt,
        undefined,
        useUtc
      )})`;
    } else {
      markdown += ` (${formatTimestampForDisplay(
        new Date(),
        undefined,
        useUtc
      )})`;
    }

    markdown += ` -->\n\n`;
  }

  const sortedConversations = sortConversationsByDate(conversations);

  for (const conversation of sortedConversations) {
    const conversationMarkdown = generateConversationMarkdown(
      conversation,
      useUtc
    );
    if (conversationMarkdown) {
      markdown += conversationMarkdown;
    }
  }

  return markdown;
}

module.exports = {
  generateMarkdown,
  generateConversationMarkdown,
  normalizeComposer,
  normalizeCursorComposer,
  normalizeVSCodeComposer,
  normalizeCursorMessage,
  normalizeVSCodeRequest,
  adaptToolUse,
  formatTimestamp,
  formatTimestampForDisplay,
  formatTimestampLocal,
  formatTimestampForFilename,
  getAgentModeString,
  MARKDOWN_VERSION,
};
