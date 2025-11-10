#!/usr/bin/env python3
# Copyright © 2025 Sierra Labs LLC
# SPDX-License-Identifier: AGPL-3.0-only
# License-Filename: LICENSE

"""
Cursor Hook: afterAgentResponse

Captures event when AI agent completes a response.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from hook_base import CursorHookBase
from shared.event_schema import HookType, EventType


class AfterAgentResponseHook(CursorHookBase):
    """Hook for after agent response."""

    def __init__(self):
        super().__init__(HookType.AFTER_AGENT_RESPONSE)

    def execute(self) -> int:
        """Execute hook logic."""
        args = self.parse_args({
            'generation_id': {'type': str, 'help': 'Generation ID'},
            'response_length': {'type': int, 'help': 'Response length in characters'},
            'tokens_used': {'type': int, 'help': 'Number of tokens used'},
            'model': {'type': str, 'help': 'Model name', 'default': None},
            'duration_ms': {'type': int, 'help': 'Response duration in ms', 'default': None},
        })

        payload = {
            'generation_id': args.generation_id,
            'response_length': args.response_length,
            'tokens_used': args.tokens_used,
            'duration_ms': args.duration_ms,
        }

        metadata = {}
        if args.model:
            metadata['model'] = args.model

        event = self.build_event(
            event_type=EventType.ASSISTANT_RESPONSE,
            payload=payload,
            metadata=metadata
        )

        self.enqueue_event(event)
        return 0


def main():
    """Main entry point."""
    hook = AfterAgentResponseHook()
    sys.exit(hook.run())


if __name__ == '__main__':
    main()
