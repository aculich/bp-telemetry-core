#!/usr/bin/env python3
# Copyright © 2025 Sierra Labs LLC
# SPDX-License-Identifier: AGPL-3.0-only
# License-Filename: LICENSE

"""
Cursor Hook: beforeSubmitPrompt

Captures event when user submits a prompt to Cursor.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hook_base import CursorHookBase
from shared.event_schema import HookType, EventType


class BeforeSubmitPromptHook(CursorHookBase):
    """Hook for before user prompt submission."""

    def __init__(self):
        super().__init__(HookType.BEFORE_SUBMIT_PROMPT)

    def execute(self) -> int:
        """Execute hook logic."""
        # Parse command-line arguments
        args = self.parse_args({
            'workspace_root': {'type': str, 'help': 'Workspace root path'},
            'generation_id': {'type': str, 'help': 'Generation ID'},
            'prompt_length': {'type': int, 'help': 'Prompt length in characters'},
        })

        # Build event payload
        payload = {
            'generation_id': args.generation_id,
            'prompt_length': args.prompt_length,
        }

        # Build and enqueue event
        event = self.build_event(
            event_type=EventType.USER_PROMPT,
            payload=payload,
            metadata={
                'workspace_root_hash': self._get_workspace_hash(),
            }
        )

        self.enqueue_event(event)
        return 0


def main():
    """Main entry point."""
    hook = BeforeSubmitPromptHook()
    sys.exit(hook.run())


if __name__ == '__main__':
    main()
