"""
End-to-end tests for Blueplane Telemetry Core.
"""

import pytest
import asyncio
import redis
import json
import uuid
from datetime import datetime

from blueplane.fast_path.consumer import FastPathConsumer
from blueplane.slow_path.worker_pool import WorkerPoolManager
from blueplane.storage.sqlite_traces import SQLiteTraceStorage
from blueplane.storage.sqlite_conversations import ConversationStorage
from blueplane.storage.redis_metrics import RedisMetricsStorage
from blueplane.config import config


@pytest.mark.asyncio
async def test_end_to_end_event_processing():
    """
    Test end-to-end event processing:
    1. Add event to Redis Streams
    2. Fast path consumes and writes to SQLite
    3. Slow path processes and updates metrics/conversations
    """
    # This is a simplified E2E test
    # Full E2E would require running the full server stack
    
    # Setup
    redis_client = redis.Redis(
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_db,
        decode_responses=True,
    )
    
    # Create test event
    test_event = {
        "event_id": str(uuid.uuid4()),
        "session_id": "e2e_test_session",
        "event_type": "tool_use",
        "platform": "claude_code",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"workspace_hash": "test123"},
        "payload": {
            "tool": "Edit",
            "duration_ms": 150,
            "tokens_used": 500,
            "lines_added": 10,
            "lines_removed": 2,
        },
    }
    
    # Add to Redis Streams
    redis_client.xadd(
        config.mq_stream_name,
        {"data": json.dumps(test_event)},
    )
    
    # Note: Full E2E test would:
    # 1. Start fast path consumer
    # 2. Wait for event to be processed
    # 3. Verify event in SQLite
    # 4. Start slow path workers
    # 5. Verify metrics/conversations updated
    # 6. Clean up
    
    # For now, just verify the event was added to stream
    messages = redis_client.xread({config.mq_stream_name: "0"}, count=1)
    assert len(messages) > 0
    
    # Cleanup
    redis_client.delete(config.mq_stream_name, config.cdc_stream_name)

