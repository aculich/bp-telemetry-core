"""
Cursor hook utilities and event builders.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, Optional

from .queue_writer import MessageQueueWriter

logger = logging.getLogger(__name__)


def build_cursor_event(
    hook_type: str,
    session_id: str,
    hook_args: Dict,
    sequence_num: Optional[int] = None,
) -> Dict:
    """
    Build a standardized telemetry event from Cursor hook arguments.
    
    Args:
        hook_type: Hook type (beforeSubmitPrompt, afterAgentResponse, etc.)
        session_id: Session ID from environment variable
        hook_args: Parsed command-line arguments
        sequence_num: Optional sequence number
    
    Returns:
        Event dictionary ready for MessageQueueWriter
    """
    event = {
        "hook_type": hook_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sequence_num": sequence_num or 0,
        "payload": hook_args,
    }
    
    # Add workspace hash if available
    workspace_hash = os.getenv("CURSOR_WORKSPACE_HASH")
    if workspace_hash:
        event["metadata"] = {"workspace_hash": workspace_hash}
    
    return event


def run_cursor_hook(hook_type: str):
    """
    Main entry point for Cursor hooks.
    
    Parses command-line arguments, gets session_id from environment,
    builds event, and writes to message queue.
    Always exits with code 0 to never block Cursor.
    
    Args:
        hook_type: Hook type name (beforeSubmitPrompt, afterAgentResponse, etc.)
    """
    try:
        # Get session_id from environment (set by Cursor extension)
        session_id = os.getenv("CURSOR_SESSION_ID")
        if not session_id:
            # Exit silently if no session_id (extension not active)
            sys.exit(0)
        
        # Parse command-line arguments (hook-specific)
        parser = argparse.ArgumentParser(description=f"Cursor {hook_type} hook")
        
        # Common arguments
        parser.add_argument("--workspace-root", type=str, help="Workspace root path")
        parser.add_argument("--generation-id", type=str, help="Generation ID")
        parser.add_argument("--prompt-length", type=int, help="Prompt length")
        parser.add_argument("--response-length", type=int, help="Response length")
        parser.add_argument("--tool-name", type=str, help="Tool name")
        parser.add_argument("--file-path", type=str, help="File path")
        parser.add_argument("--file-extension", type=str, help="File extension")
        parser.add_argument("--lines-added", type=int, help="Lines added")
        parser.add_argument("--lines-removed", type=int, help="Lines removed")
        parser.add_argument("--command", type=str, help="Shell command")
        parser.add_argument("--exit-code", type=int, help="Exit code")
        
        # Parse args (ignore unknown args to be flexible)
        args, unknown = parser.parse_known_args()
        
        # Convert args to dict (only non-None values)
        hook_args = {
            k: v for k, v in vars(args).items() if v is not None
        }
        
        # Add any additional data from unknown args as JSON
        if unknown:
            # Try to parse as JSON if it looks like JSON
            for arg in unknown:
                if arg.startswith("{") or arg.startswith("["):
                    try:
                        hook_args.update(json.loads(arg))
                    except json.JSONDecodeError:
                        pass
        
        # Build event
        event = build_cursor_event(
            hook_type=hook_type,
            session_id=session_id,
            hook_args=hook_args,
        )
        
        # Write to message queue
        writer = MessageQueueWriter()
        success = writer.enqueue(
            event=event,
            platform="cursor",
            session_id=session_id,
            hook_type=hook_type,
        )
        
        if not success:
            logger.debug(f"Failed to enqueue {hook_type} event (silent failure)")
        
        # Always exit 0 (never block Cursor)
        sys.exit(0)
        
    except Exception as e:
        logger.debug(f"Error in Cursor hook {hook_type}: {e}", exc_info=True)
        sys.exit(0)  # Always exit 0, never block


# Hook entry points (these would be called by individual hook scripts)
def before_submit_prompt():
    """beforeSubmitPrompt hook entry point."""
    run_cursor_hook("beforeSubmitPrompt")


def after_agent_response():
    """afterAgentResponse hook entry point."""
    run_cursor_hook("afterAgentResponse")


def before_mcp_execution():
    """beforeMCPExecution hook entry point."""
    run_cursor_hook("beforeMCPExecution")


def after_mcp_execution():
    """afterMCPExecution hook entry point."""
    run_cursor_hook("afterMCPExecution")


def after_file_edit():
    """afterFileEdit hook entry point."""
    run_cursor_hook("afterFileEdit")


def before_shell_execution():
    """beforeShellExecution hook entry point."""
    run_cursor_hook("beforeShellExecution")


def after_shell_execution():
    """afterShellExecution hook entry point."""
    run_cursor_hook("afterShellExecution")


def before_read_file():
    """beforeReadFile hook entry point."""
    run_cursor_hook("beforeReadFile")


def stop():
    """stop hook entry point."""
    run_cursor_hook("stop")

