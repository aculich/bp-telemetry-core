#!/usr/bin/env python3
# Copyright © 2025 Sierra Labs LLC
# SPDX-License-Identifier: AGPL-3.0-only
# License-Filename: LICENSE

"""
Cursor Hook: stop

Captures event when session terminates.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from hook_base import CursorHookBase
from shared.event_schema import HookType, EventType


class StopHook(CursorHookBase):
    """Hook for session stop."""

    def __init__(self):
        super().__init__(HookType.CURSOR_STOP)

    def execute(self) -> int:
        """Execute hook logic."""
        args = self.parse_args({
            'session_duration_ms': {'type': int, 'help': 'Session duration in milliseconds', 'default': 0},
        })

        payload = {
            'session_duration_ms': args.session_duration_ms,
        }

        event = self.build_event(
            event_type=EventType.SESSION_END,
            payload=payload
        )

        self.enqueue_event(event)
        return 0


def main():
    """Main entry point."""
    hook = StopHook()
    sys.exit(hook.run())


if __name__ == '__main__':
    main()
