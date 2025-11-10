"""
Unit tests for storage layer.
"""

import pytest
import json
import uuid
from datetime import datetime

from blueplane.storage.sqlite_traces import SQLiteTraceStorage
from blueplane.storage.sqlite_conversations import ConversationStorage


class TestSQLiteTraceStorage:
    """Test SQLite trace storage."""

    def test_batch_insert(self, sqlite_trace_storage):
        """Test batch insert of events."""
        events = [
            {
                "event_id": str(uuid.uuid4()),
                "session_id": "test_session_1",
                "event_type": "tool_use",
                "platform": "claude_code",
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {"workspace_hash": "abc123"},
                "payload": {"tool": "Edit", "duration_ms": 100},
            },
            {
                "event_id": str(uuid.uuid4()),
                "session_id": "test_session_1",
                "event_type": "user_prompt",
                "platform": "claude_code",
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {},
                "payload": {},
            },
        ]
        
        sqlite_trace_storage.batch_insert(events)
        
        # Verify events were inserted
        session_events = sqlite_trace_storage.get_session_events("test_session_1")
        assert len(session_events) == 2
        assert session_events[0]["event_type"] == "tool_use"
        assert session_events[1]["event_type"] == "user_prompt"

    def test_get_by_sequence(self, sqlite_trace_storage):
        """Test getting event by sequence number."""
        event = {
            "event_id": str(uuid.uuid4()),
            "session_id": "test_session_2",
            "event_type": "session_start",
            "platform": "cursor",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {},
            "payload": {},
        }
        
        sqlite_trace_storage.batch_insert([event])
        
        # Get by sequence (should be 1 for first insert)
        retrieved = sqlite_trace_storage.get_by_sequence(1)
        assert retrieved is not None
        assert retrieved["event_id"] == event["event_id"]
        assert retrieved["session_id"] == "test_session_2"

    def test_calculate_session_metrics(self, sqlite_trace_storage):
        """Test session metrics calculation."""
        events = [
            {
                "event_id": str(uuid.uuid4()),
                "session_id": "test_session_3",
                "event_type": "tool_use",
                "platform": "claude_code",
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {},
                "payload": {"duration_ms": 150, "tokens_used": 1000, "lines_added": 10},
            },
        ]
        
        sqlite_trace_storage.batch_insert(events)
        
        metrics = sqlite_trace_storage.calculate_session_metrics("test_session_3")
        assert metrics["event_count"] == 1
        assert metrics["total_tokens"] == 1000
        assert metrics["total_lines_added"] == 10


class TestConversationStorage:
    """Test conversation storage."""

    def test_create_conversation(self, conversation_storage):
        """Test creating a conversation."""
        conv_id = conversation_storage.create_conversation(
            session_id="test_session",
            external_session_id="ext_session_1",
            platform="claude_code",
            workspace_hash="abc123",
        )
        
        assert conv_id is not None
        
        # Verify conversation exists
        conversations = conversation_storage.get_conversations_by_session("test_session")
        assert len(conversations) == 1
        assert conversations[0]["id"] == conv_id

    def test_add_turn(self, conversation_storage):
        """Test adding a turn to a conversation."""
        conv_id = conversation_storage.create_conversation(
            session_id="test_session",
            external_session_id="ext_session_2",
            platform="claude_code",
        )
        
        turn_id = conversation_storage.add_turn(
            conversation_id=conv_id,
            turn_type="user_prompt",
            content_hash="hash123",
            tokens_used=50,
            latency_ms=100,
        )
        
        assert turn_id is not None
        
        # Verify turn was added
        conversation = conversation_storage.get_conversation_flow(conv_id)
        assert len(conversation["turns"]) == 1
        assert conversation["turns"][0]["turn_type"] == "user_prompt"

    def test_track_code_change(self, conversation_storage):
        """Test tracking code changes."""
        conv_id = conversation_storage.create_conversation(
            session_id="test_session",
            external_session_id="ext_session_3",
            platform="claude_code",
        )
        
        change_id = conversation_storage.track_code_change(
            conversation_id=conv_id,
            turn_id=None,
            file_extension=".py",
            operation="edit",
            lines_added=5,
            lines_removed=2,
            accepted=True,
            acceptance_delay_ms=500,
        )
        
        assert change_id is not None
        
        # Verify change was tracked
        conversation = conversation_storage.get_conversation_flow(conv_id)
        assert len(conversation["code_changes"]) == 1
        assert conversation["code_changes"][0]["file_extension"] == ".py"
        assert conversation["code_changes"][0]["accepted"] == True

