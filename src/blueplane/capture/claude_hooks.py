"""
Claude Code hook utilities and event builders.
"""

import json
import sys
import logging
from datetime import datetime
from typing import Dict, Optional

from .queue_writer import MessageQueueWriter

logger = logging.getLogger(__name__)


def build_claude_event(
    hook_type: str,
    session_id: str,
    hook_data: Dict,
    sequence_num: Optional[int] = None,
) -> Dict:
    """
    Build a standardized telemetry event from Claude Code hook data.
    
    Args:
        hook_type: Hook type (SessionStart, PreToolUse, PostToolUse, etc.)
        session_id: Session ID provided by Claude Code
        hook_data: Raw hook data from Claude Code
        sequence_num: Optional sequence number
    
    Returns:
        Event dictionary ready for MessageQueueWriter
    """
    event = {
        "hook_type": hook_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sequence_num": sequence_num or 0,
        "payload": hook_data,
    }
    
    # Extract metadata if present
    if "metadata" in hook_data:
        event["metadata"] = hook_data["metadata"]
    
    return event


def run_claude_hook(hook_type: str):
    """
    Main entry point for Claude Code hooks.
    
    Reads JSON from stdin, builds event, and writes to message queue.
    Always exits with code 0 to never block Claude Code.
    
    Args:
        hook_type: Hook type name (SessionStart, PreToolUse, etc.)
    """
    try:
        # Read JSON from stdin
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            # Empty input - exit silently
            sys.exit(0)
        
        hook_data = json.loads(stdin_data)
        
        # Extract session_id from hook data (Claude Code provides this)
        session_id = hook_data.get("session_id") or hook_data.get("sessionId")
        if not session_id:
            logger.debug(f"No session_id in hook data for {hook_type}")
            sys.exit(0)  # Exit silently if no session
        
        # Build event
        sequence_num = hook_data.get("sequence_num") or hook_data.get("sequenceNum")
        event = build_claude_event(
            hook_type=hook_type,
            session_id=session_id,
            hook_data=hook_data,
            sequence_num=sequence_num,
        )
        
        # Write to message queue
        writer = MessageQueueWriter()
        success = writer.enqueue(
            event=event,
            platform="claude_code",
            session_id=session_id,
            hook_type=hook_type,
        )
        
        if not success:
            logger.debug(f"Failed to enqueue {hook_type} event (silent failure)")
        
        # Always exit 0 (never block Claude Code)
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        logger.debug(f"Invalid JSON in hook input: {e}")
        sys.exit(0)  # Exit silently on JSON errors
    except Exception as e:
        logger.debug(f"Error in Claude hook {hook_type}: {e}", exc_info=True)
        sys.exit(0)  # Always exit 0, never block


# Hook entry points (these would be called by individual hook scripts)
def session_start():
    """SessionStart hook entry point."""
    run_claude_hook("SessionStart")


def pre_tool_use():
    """PreToolUse hook entry point."""
    run_claude_hook("PreToolUse")


def post_tool_use():
    """PostToolUse hook entry point."""
    run_claude_hook("PostToolUse")


def user_prompt_submit():
    """UserPromptSubmit hook entry point."""
    run_claude_hook("UserPromptSubmit")


def stop():
    """Stop hook entry point."""
    run_claude_hook("Stop")


def pre_compact():
    """PreCompact hook entry point."""
    run_claude_hook("PreCompact")

