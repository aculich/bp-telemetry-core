# Copyright © 2025 Sierra Labs LLC
# SPDX-License-Identifier: AGPL-3.0-only
# License-Filename: LICENSE

"""
Base utilities for Cursor hooks.

Provides common functionality for all Cursor hook scripts.
"""

import os
import sys
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.queue_writer import MessageQueueWriter
from shared.event_schema import Platform, HookType, EventType


class CursorHookBase:
    """
    Base class for Cursor hooks.

    Provides common functionality:
    - Environment variable reading
    - Session ID retrieval
    - Event building
    - Message queue integration
    - Silent failure mode
    """

    def __init__(self, hook_type: HookType):
        """
        Initialize hook.

        Args:
            hook_type: Type of hook being executed
        """
        self.hook_type = hook_type
        self.session_id = self._get_session_id()
        self.workspace_root = None
        self.queue_writer = None

        # Only initialize queue writer if we have a session
        if self.session_id:
            try:
                self.queue_writer = MessageQueueWriter()
            except Exception:
                # Silent failure - don't block IDE
                pass

    def _get_session_id(self) -> Optional[str]:
        """
        Get session ID from environment variable.

        Returns:
            Session ID or None if not set
        """
        return os.environ.get('CURSOR_SESSION_ID')

    def _get_workspace_hash(self) -> Optional[str]:
        """
        Get workspace hash from environment variable.

        Returns:
            Workspace hash or None if not set
        """
        return os.environ.get('CURSOR_WORKSPACE_HASH')

    def parse_args(self, args_spec: Dict[str, Dict[str, Any]]) -> argparse.Namespace:
        """
        Parse command-line arguments.

        Args:
            args_spec: Dictionary of argument specifications
                      Format: {arg_name: {type: str, help: str, default: None}}

        Returns:
            Parsed arguments namespace
        """
        parser = argparse.ArgumentParser(description=f"Cursor {self.hook_type.value} hook")

        for arg_name, spec in args_spec.items():
            arg_type = spec.get('type', str)
            arg_help = spec.get('help', '')
            arg_default = spec.get('default')

            parser.add_argument(
                f'--{arg_name.replace("_", "-")}',
                dest=arg_name,
                type=arg_type,
                help=arg_help,
                default=arg_default
            )

        return parser.parse_args()

    def build_event(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build event dictionary.

        Args:
            event_type: Type of event
            payload: Event payload data
            metadata: Additional metadata

        Returns:
            Event dictionary
        """
        event = {
            'hook_type': self.hook_type.value,
            'event_type': event_type.value,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'payload': payload,
            'metadata': metadata or {},
        }

        # Add workspace hash if available
        workspace_hash = self._get_workspace_hash()
        if workspace_hash:
            event['metadata']['workspace_hash'] = workspace_hash

        return event

    def enqueue_event(self, event: Dict[str, Any]) -> bool:
        """
        Enqueue event to message queue.

        Args:
            event: Event dictionary

        Returns:
            True on success, False on failure (silent)
        """
        if not self.session_id:
            # No session active - skip silently
            return False

        if not self.queue_writer:
            # Queue writer not initialized - skip silently
            return False

        try:
            return self.queue_writer.enqueue(
                event=event,
                platform=Platform.CURSOR.value,
                session_id=self.session_id
            )
        except Exception:
            # Silent failure - never block IDE
            return False

    def execute(self) -> int:
        """
        Execute hook (to be implemented by subclasses).

        Returns:
            Exit code (always 0 for hooks)
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def run(self) -> int:
        """
        Run hook with error handling.

        Returns:
            Always returns 0 (success) - never fails
        """
        try:
            return self.execute()
        except Exception:
            # Silent failure - always return success
            return 0
