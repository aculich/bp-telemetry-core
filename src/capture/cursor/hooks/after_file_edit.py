#!/usr/bin/env python3
# Copyright © 2025 Sierra Labs LLC
# SPDX-License-Identifier: AGPL-3.0-only
# License-Filename: LICENSE

"""
Cursor Hook: afterFileEdit

Captures event after a file is edited.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from hook_base import CursorHookBase
from shared.event_schema import HookType, EventType


class AfterFileEditHook(CursorHookBase):
    """Hook for after file edit."""

    def __init__(self):
        super().__init__(HookType.AFTER_FILE_EDIT)

    def execute(self) -> int:
        """Execute hook logic."""
        args = self.parse_args({
            'file_extension': {'type': str, 'help': 'File extension', 'default': None},
            'lines_added': {'type': int, 'help': 'Number of lines added'},
            'lines_removed': {'type': int, 'help': 'Number of lines removed'},
            'operation': {'type': str, 'help': 'Operation type (create, edit, delete)', 'default': 'edit'},
            'generation_id': {'type': str, 'help': 'Generation ID', 'default': None},
        })

        payload = {
            'file_extension': args.file_extension,
            'lines_added': args.lines_added,
            'lines_removed': args.lines_removed,
            'operation': args.operation,
            'generation_id': args.generation_id,
        }

        event = self.build_event(
            event_type=EventType.FILE_EDIT,
            payload=payload
        )

        self.enqueue_event(event)
        return 0


def main():
    """Main entry point."""
    hook = AfterFileEditHook()
    sys.exit(hook.run())


if __name__ == '__main__':
    main()
