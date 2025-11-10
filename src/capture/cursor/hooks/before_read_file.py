#!/usr/bin/env python3
# Copyright © 2025 Sierra Labs LLC
# SPDX-License-Identifier: AGPL-3.0-only
# License-Filename: LICENSE

"""
Cursor Hook: beforeReadFile

Captures event before reading a file.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from hook_base import CursorHookBase
from shared.event_schema import HookType, EventType


class BeforeReadFileHook(CursorHookBase):
    """Hook for before file read."""

    def __init__(self):
        super().__init__(HookType.BEFORE_READ_FILE)

    def execute(self) -> int:
        """Execute hook logic."""
        args = self.parse_args({
            'file_extension': {'type': str, 'help': 'File extension', 'default': None},
            'file_size': {'type': int, 'help': 'File size in bytes', 'default': 0},
        })

        payload = {
            'file_extension': args.file_extension,
            'file_size': args.file_size,
        }

        event = self.build_event(
            event_type=EventType.FILE_READ,
            payload=payload
        )

        self.enqueue_event(event)
        return 0


def main():
    """Main entry point."""
    hook = BeforeReadFileHook()
    sys.exit(hook.run())


if __name__ == '__main__':
    main()
