"""
Integration tests for slow path workers.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from blueplane.slow_path.metrics_worker import MetricsWorker
from blueplane.slow_path.conversation_worker import ConversationWorker
from blueplane.storage.redis_cdc import CDCWorkQueue
from blueplane.storage.sqlite_traces import SQLiteTraceStorage
from blueplane.storage.sqlite_conversations import ConversationStorage


@pytest.mark.asyncio
async def test_metrics_worker_process():
    """Test metrics worker processing events."""
    # Create mock storage
    trace_storage = Mock(spec=SQLiteTraceStorage)
    metrics_storage = Mock()
    
    # Mock event
    mock_event = {
        "sequence": 1,
        "event_id": "test_event",
        "session_id": "test_session",
        "event_type": "tool_use",
        "platform": "claude_code",
        "timestamp": "2025-01-01T00:00:00Z",
        "duration_ms": 100,
        "payload": {"tool": "Edit", "duration_ms": 100},
    }
    
    trace_storage.get_by_sequence.return_value = mock_event
    
    worker = MetricsWorker(
        cdc_queue=Mock(),
        worker_name="test-worker",
        trace_storage=trace_storage,
        metrics_storage=metrics_storage,
    )
    
    cdc_event = {
        "sequence": 1,
        "event_id": "test_event",
        "session_id": "test_session",
        "event_type": "tool_use",
    }
    
    await worker.process(cdc_event)
    
    # Verify metrics were recorded
    assert metrics_storage.record_metric.called or metrics_storage.increment_counter.called


@pytest.mark.asyncio
async def test_conversation_worker_process():
    """Test conversation worker processing events."""
    trace_storage = Mock(spec=SQLiteTraceStorage)
    conversation_storage = Mock(spec=ConversationStorage)
    
    mock_event = {
        "sequence": 1,
        "event_id": "test_event",
        "session_id": "test_session",
        "external_session_id": "ext_session",
        "event_type": "user_prompt",
        "platform": "claude_code",
        "timestamp": "2025-01-01T00:00:00Z",
        "metadata": {},
        "payload": {"content": "test prompt"},
    }
    
    trace_storage.get_by_sequence.return_value = mock_event
    conversation_storage.get_or_create_conversation.return_value = "conv_id"
    
    worker = ConversationWorker(
        cdc_queue=Mock(),
        worker_name="test-worker",
        trace_storage=trace_storage,
        conversation_storage=conversation_storage,
    )
    
    cdc_event = {
        "sequence": 1,
        "event_id": "test_event",
        "session_id": "test_session",
        "event_type": "user_prompt",
    }
    
    await worker.process(cdc_event)
    
    # Verify conversation was created/updated
    assert conversation_storage.get_or_create_conversation.called
    assert conversation_storage.add_turn.called

