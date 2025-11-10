#!/usr/bin/env python3
# Copyright © 2025 Sierra Labs LLC
# SPDX-License-Identifier: AGPL-3.0-only
# License-Filename: LICENSE

"""
Cursor Hook: beforeShellExecution

Captures event before shell command execution.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from hook_base import CursorHookBase
from shared.event_schema import HookType, EventType


class BeforeShellExecutionHook(CursorHookBase):
    """Hook for before shell execution."""

    def __init__(self):
        super().__init__(HookType.BEFORE_SHELL_EXECUTION)

    def execute(self) -> int:
        """Execute hook logic."""
        args = self.parse_args({
            'command_length': {'type': int, 'help': 'Command length in characters'},
            'generation_id': {'type': str, 'help': 'Generation ID', 'default': None},
        })

        payload = {
            'command_length': args.command_length,
            'generation_id': args.generation_id,
        }

        event = self.build_event(
            event_type=EventType.SHELL_EXECUTION,
            payload=payload
        )

        self.enqueue_event(event)
        return 0


def main():
    """Main entry point."""
    hook = BeforeShellExecutionHook()
    sys.exit(hook.run())


if __name__ == '__main__':
    main()
