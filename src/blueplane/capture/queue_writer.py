"""
Message Queue Writer - Shared component for writing events to Redis Streams.
Used by both Claude Code and Cursor hooks.
"""

import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Optional
import redis
from redis.connection import ConnectionPool

from ..config import config

logger = logging.getLogger(__name__)


class MessageQueueWriter:
    """
    Write events to Redis Streams message queue.
    
    Shared by all platforms (Claude Code, Cursor) to write telemetry events.
    Designed to fail silently to prevent blocking IDE operations.
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize Redis connection.
        
        Args:
            redis_client: Optional Redis client (for testing). If None, creates new connection.
        """
        if redis_client:
            self.redis = redis_client
        else:
            # Create connection pool for performance
            pool = ConnectionPool(
                host=config.redis_host,
                port=config.redis_port,
                db=config.redis_db,
                decode_responses=True,
                socket_connect_timeout=1,  # 1 second timeout
                socket_timeout=1,
            )
            self.redis = redis.Redis(connection_pool=pool)
        
        self.stream_name = config.mq_stream_name
        self.maxlen = 10000  # Approximate max length for auto-trimming

    def enqueue(
        self,
        event: Dict,
        platform: str,
        session_id: str,
        hook_type: Optional[str] = None,
    ) -> bool:
        """
        Write event to Redis Streams telemetry:events.
        
        Args:
            event: Event dictionary with hook_type, timestamp, payload, etc.
            platform: Platform identifier ('claude_code' or 'cursor')
            session_id: External session ID (platform-native)
            hook_type: Hook type (if not in event dict)
        
        Returns:
            True on success, False on failure (silent failure to not block IDE)
        """
        try:
            # Generate event ID
            event_id = str(uuid.uuid4())
            
            # Extract hook_type from event or use provided
            hook_type = hook_type or event.get("hook_type", "unknown")
            
            # Extract timestamp from event or use current time
            timestamp = event.get("timestamp") or datetime.utcnow().isoformat() + "Z"
            
            # Extract sequence number if present
            sequence_num = str(event.get("sequence_num", "0"))
            
            # Serialize payload/data
            payload = event.get("payload") or event.get("data") or {}
            data_json = json.dumps(payload) if payload else "{}"
            
            # Build Redis stream entry (flat key-value pairs)
            stream_entry = {
                "event_id": event_id,
                "enqueued_at": datetime.utcnow().isoformat() + "Z",
                "retry_count": "0",
                "platform": platform,
                "external_session_id": session_id,
                "hook_type": hook_type,
                "timestamp": timestamp,
                "sequence_num": sequence_num,
                "data": data_json,
            }
            
            # Add any additional metadata
            if "metadata" in event:
                stream_entry["metadata"] = json.dumps(event["metadata"])
            
            # Write to Redis Streams with auto-trim
            self.redis.xadd(
                name=self.stream_name,
                fields=stream_entry,
                maxlen=self.maxlen,
                approximate=True,  # Efficient approximate trimming
            )
            
            return True
            
        except (redis.ConnectionError, redis.TimeoutError, redis.RedisError) as e:
            # Log error but don't raise (silent failure)
            # Hooks must never block IDE operations
            logger.debug(f"Failed to enqueue event to Redis: {e}", exc_info=True)
            return False
        except Exception as e:
            # Catch-all for any other errors
            logger.debug(f"Unexpected error enqueueing event: {e}", exc_info=True)
            return False

    def test_connection(self) -> bool:
        """
        Test Redis connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.redis.ping()
            return True
        except Exception:
            return False

