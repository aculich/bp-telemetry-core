#!/usr/bin/env python3
# Copyright © 2025 Sierra Labs LLC
# SPDX-License-Identifier: AGPL-3.0-only
# License-Filename: LICENSE

"""
Cursor Hook: afterShellExecution

Captures event after shell command execution completes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from hook_base import CursorHookBase
from shared.event_schema import HookType, EventType


class AfterShellExecutionHook(CursorHookBase):
    """Hook for after shell execution."""

    def __init__(self):
        super().__init__(HookType.AFTER_SHELL_EXECUTION)

    def execute(self) -> int:
        """Execute hook logic."""
        args = self.parse_args({
            'exit_code': {'type': int, 'help': 'Command exit code'},
            'duration_ms': {'type': int, 'help': 'Execution duration in milliseconds'},
            'output_lines': {'type': int, 'help': 'Number of output lines', 'default': 0},
        })

        payload = {
            'exit_code': args.exit_code,
            'duration_ms': args.duration_ms,
            'output_lines': args.output_lines,
            'success': args.exit_code == 0,
        }

        event = self.build_event(
            event_type=EventType.SHELL_EXECUTION,
            payload=payload
        )

        self.enqueue_event(event)
        return 0


def main():
    """Main entry point."""
    hook = AfterShellExecutionHook()
    sys.exit(hook.run())


if __name__ == '__main__':
    main()
