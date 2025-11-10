#!/usr/bin/env python3
# Copyright © 2025 Sierra Labs LLC
# SPDX-License-Identifier: AGPL-3.0-only
# License-Filename: LICENSE

"""
Cursor Hook: beforeMCPExecution

Captures event before MCP tool execution.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from hook_base import CursorHookBase
from shared.event_schema import HookType, EventType


class BeforeMCPExecutionHook(CursorHookBase):
    """Hook for before MCP tool execution."""

    def __init__(self):
        super().__init__(HookType.BEFORE_MCP_EXECUTION)

    def execute(self) -> int:
        """Execute hook logic."""
        args = self.parse_args({
            'tool_name': {'type': str, 'help': 'MCP tool name'},
            'input_size': {'type': int, 'help': 'Input size in bytes', 'default': 0},
            'generation_id': {'type': str, 'help': 'Generation ID', 'default': None},
        })

        payload = {
            'tool_name': args.tool_name,
            'input_size': args.input_size,
            'generation_id': args.generation_id,
        }

        event = self.build_event(
            event_type=EventType.MCP_EXECUTION,
            payload=payload
        )

        self.enqueue_event(event)
        return 0


def main():
    """Main entry point."""
    hook = BeforeMCPExecutionHook()
    sys.exit(hook.run())


if __name__ == '__main__':
    main()
