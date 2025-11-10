#!/usr/bin/env python3
"""
Test script to simulate Claude Code events for testing telemetry capture.
This simulates what would happen when using Claude Code with hooks installed.
"""

import json
import redis
import uuid
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from blueplane.capture import MessageQueueWriter
from blueplane.config import config


def simulate_session_start(writer: MessageQueueWriter, session_id: str):
    """Simulate SessionStart hook."""
    event = {
        "hook_type": "SessionStart",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sequence_num": 1,
        "payload": {
            "cwd": "/Users/me/projects/test-project",
            "transcript_path": f"/tmp/test-transcript-{session_id}.jsonl",
            "workspace_hash": "abc123def456",
        },
    }
    writer.enqueue(event, "claude_code", session_id, "SessionStart")
    print(f"✅ SessionStart event sent")


def simulate_user_prompt(writer: MessageQueueWriter, session_id: str, prompt: str, seq: int):
    """Simulate UserPromptSubmit hook."""
    event = {
        "hook_type": "UserPromptSubmit",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sequence_num": seq,
        "payload": {
            "prompt_length": len(prompt),
            "prompt_hash": str(hash(prompt))[:16],
        },
    }
    writer.enqueue(event, "claude_code", session_id, "UserPromptSubmit")
    print(f"✅ UserPromptSubmit event sent (seq={seq})")


def simulate_tool_use(writer: MessageQueueWriter, session_id: str, tool: str, seq: int, accepted: bool = True):
    """Simulate PreToolUse / PostToolUse hooks."""
    # PreToolUse
    pre_event = {
        "hook_type": "PreToolUse",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sequence_num": seq,
        "payload": {
            "tool": tool,
            "tool_id": str(uuid.uuid4()),
        },
    }
    writer.enqueue(pre_event, "claude_code", session_id, "PreToolUse")
    
    # PostToolUse (simulate some delay)
    import time
    time.sleep(0.1)
    
    post_event = {
        "hook_type": "PostToolUse",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sequence_num": seq + 1,
        "payload": {
            "tool": tool,
            "duration_ms": 150,
            "tokens_used": 500,
            "accepted": accepted,
            "lines_added": 10 if tool == "Edit" else 0,
            "lines_removed": 2 if tool == "Edit" else 0,
        },
    }
    writer.enqueue(post_event, "claude_code", session_id, "PostToolUse")
    print(f"✅ ToolUse event sent: {tool} (accepted={accepted}, seq={seq})")


def simulate_stop(writer: MessageQueueWriter, session_id: str, seq: int):
    """Simulate Stop hook."""
    event = {
        "hook_type": "Stop",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sequence_num": seq,
        "payload": {
            "reason": "user_stop",
        },
    }
    writer.enqueue(event, "claude_code", session_id, "Stop")
    print(f"✅ Stop event sent")


def test_sample_case_1_refactoring():
    """Sample Case 1: Refactoring with Multiple Tools"""
    print("\n" + "="*60)
    print("Sample Case 1: Refactoring with Multiple Tools")
    print("="*60)
    
    session_id = f"test-refactor-{uuid.uuid4().hex[:8]}"
    writer = MessageQueueWriter()
    
    simulate_session_start(writer, session_id)
    
    simulate_user_prompt(writer, session_id, "Refactor this class to use dependency injection", 2)
    simulate_tool_use(writer, session_id, "ReadFile", 3)
    simulate_tool_use(writer, session_id, "Edit", 4, accepted=True)
    simulate_tool_use(writer, session_id, "ReadFile", 5)
    
    simulate_user_prompt(writer, session_id, "Add unit tests for the refactored class", 6)
    simulate_tool_use(writer, session_id, "Edit", 7, accepted=True)
    
    simulate_stop(writer, session_id, 8)
    
    print(f"\n✅ Sample Case 1 complete (session_id: {session_id})")
    return session_id


def test_sample_case_2_bug_fix():
    """Sample Case 2: Bug Fix with Rejection Pattern"""
    print("\n" + "="*60)
    print("Sample Case 2: Bug Fix with Rejection Pattern")
    print("="*60)
    
    session_id = f"test-bugfix-{uuid.uuid4().hex[:8]}"
    writer = MessageQueueWriter()
    
    simulate_session_start(writer, session_id)
    
    simulate_user_prompt(writer, session_id, "Fix the bug where the function returns None", 2)
    simulate_tool_use(writer, session_id, "Edit", 3, accepted=False)  # First attempt rejected
    
    simulate_user_prompt(writer, session_id, "Actually, I need it to return an empty list, not None", 4)
    simulate_tool_use(writer, session_id, "Edit", 5, accepted=True)  # Second attempt accepted
    
    simulate_stop(writer, session_id, 6)
    
    print(f"\n✅ Sample Case 2 complete (session_id: {session_id})")
    return session_id


def test_sample_case_3_multi_file():
    """Sample Case 3: Multi-File Feature Addition"""
    print("\n" + "="*60)
    print("Sample Case 3: Multi-File Feature Addition")
    print("="*60)
    
    session_id = f"test-multifile-{uuid.uuid4().hex[:8]}"
    writer = MessageQueueWriter()
    
    simulate_session_start(writer, session_id)
    
    simulate_user_prompt(writer, session_id, "Add a new authentication feature", 2)
    simulate_tool_use(writer, session_id, "Edit", 3, accepted=True)  # auth.py
    simulate_tool_use(writer, session_id, "Edit", 4, accepted=True)  # routes.py
    simulate_tool_use(writer, session_id, "Edit", 5, accepted=True)  # config.py
    simulate_tool_use(writer, session_id, "ReadFile", 6)  # Verify integration
    
    simulate_user_prompt(writer, session_id, "Add documentation for the new feature", 7)
    simulate_tool_use(writer, session_id, "Edit", 8, accepted=True)  # README.md
    
    simulate_stop(writer, session_id, 9)
    
    print(f"\n✅ Sample Case 3 complete (session_id: {session_id})")
    return session_id


def main():
    """Run all sample test cases."""
    print("="*60)
    print("Blueplane Telemetry Core - Sample Test Cases")
    print("="*60)
    print("\nThis script simulates Claude Code events for testing.")
    print("Make sure Redis is running and processing server is started.\n")
    
    # Test connection
    writer = MessageQueueWriter()
    if not writer.test_connection():
        print("❌ Redis connection failed. Please start Redis:")
        print("   brew services start redis")
        return 1
    
    print("✅ Redis connection successful\n")
    
    # Run sample cases
    sessions = []
    sessions.append(test_sample_case_1_refactoring())
    import time
    time.sleep(1)
    
    sessions.append(test_sample_case_2_bug_fix())
    time.sleep(1)
    
    sessions.append(test_sample_case_3_multi_file())
    
    print("\n" + "="*60)
    print("All Sample Cases Complete!")
    print("="*60)
    print(f"\nGenerated {len(sessions)} test sessions:")
    for i, session_id in enumerate(sessions, 1):
        print(f"  {i}. {session_id}")
    
    print("\nNext steps:")
    print("  1. Wait a few seconds for processing")
    print("  2. Check metrics: blueplane metrics")
    print("  3. List sessions: blueplane sessions")
    print("  4. Analyze session: blueplane analyze <session_id>")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

