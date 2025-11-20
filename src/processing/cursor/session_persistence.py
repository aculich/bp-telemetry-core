# Copyright © 2025 Sierra Labs LLC
# SPDX-License-Identifier: AGPL-3.0-only
# License-Filename: LICENSE

"""
Session Persistence Module for Cursor.

Manages persistent session state in SQLite database, providing durability
and recovery capabilities for Cursor session management.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from ..database.sqlite_client import SQLiteClient

logger = logging.getLogger(__name__)


class CursorSessionPersistence:
    """
    Manages persistent session state in SQLite database for Cursor.
    
    Provides durability and recovery capabilities for session lifecycle management.
    """

    def __init__(self, sqlite_client: SQLiteClient):
        """
        Initialize session persistence.

        Args:
            sqlite_client: SQLiteClient instance for database operations
        """
        self.sqlite_client = sqlite_client

    async def save_session_start(
        self,
        external_session_id: str,
        workspace_hash: str,
        workspace_path: str = '',
        workspace_name: str = '',
        metadata: Optional[dict] = None
    ) -> str:
        """
        Persist new Cursor session to cursor_sessions table.
        
        Called when session_start event is received.

        Args:
            external_session_id: Session ID from Cursor extension
            workspace_hash: Hash of workspace path
            workspace_path: Full workspace path
            workspace_name: Human-readable workspace name
            metadata: Additional session metadata

        Returns:
            Internal session ID (UUID)
        """
        import uuid
        
        try:
            # Generate internal session ID
            internal_session_id = str(uuid.uuid4())
            
            # Prepare metadata JSON
            session_metadata = {
                'source': 'extension',
                'started_via': 'session_start_event',
                'workspace_path': workspace_path,
                'workspace_name': workspace_name,
                'workspace_hash': workspace_hash,
                **(metadata or {})
            }
            
            # Insert into cursor_sessions table
            # Use INSERT OR IGNORE to avoid overwriting existing sessions
            # If session already exists, get its internal ID
            with self.sqlite_client.get_connection() as conn:
                # Check if session already exists
                cursor = conn.execute("""
                    SELECT id FROM cursor_sessions
                    WHERE external_session_id = ?
                """, (external_session_id,))
                
                existing = cursor.fetchone()
                if existing:
                    # Session already exists, return existing internal ID
                    internal_session_id = existing[0]
                    logger.debug(f"Cursor session {external_session_id} already exists, using existing internal ID: {internal_session_id}")
                else:
                    # Insert new session
                    cursor = conn.execute("""
                        INSERT INTO cursor_sessions (
                            id, external_session_id, workspace_hash,
                            workspace_name, workspace_path, started_at, metadata
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        internal_session_id,
                        external_session_id,
                        workspace_hash,
                        workspace_name,
                        workspace_path,
                        datetime.now(timezone.utc).isoformat(),
                        json.dumps(session_metadata),
                    ))
                    conn.commit()
                    logger.info(f"Persisted Cursor session start: {external_session_id} -> {internal_session_id}")
                
            return internal_session_id

        except Exception as e:
            logger.error(f"Failed to persist session start for {external_session_id}: {e}", exc_info=True)
            # Don't raise - allow in-memory tracking to continue
            raise

    async def save_session_end(
        self,
        external_session_id: str,
        end_reason: str = 'normal'  # 'normal', 'timeout', 'crash'
    ) -> None:
        """
        Mark Cursor session as ended with timestamp and reason.
        
        Called when session_end event is received.

        Args:
            external_session_id: Session ID from Cursor extension
            end_reason: Reason for session end ('normal', 'timeout', 'crash')
        """
        try:
            with self.sqlite_client.get_connection() as conn:
                # Update ended_at timestamp
                cursor = conn.execute("""
                    UPDATE cursor_sessions
                    SET ended_at = ?
                    WHERE external_session_id = ?
                """, (
                    datetime.now(timezone.utc).isoformat(),
                    external_session_id
                ))
                
                if cursor.rowcount == 0:
                    logger.warning(f"Session {external_session_id} not found in cursor_sessions table for end update")
                else:
                    # Update metadata with end reason
                    cursor = conn.execute("""
                        SELECT metadata FROM cursor_sessions
                        WHERE external_session_id = ?
                    """, (external_session_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        try:
                            metadata = json.loads(row[0]) if row[0] else {}
                            metadata['end_reason'] = end_reason
                            metadata['ended_at'] = datetime.now(timezone.utc).isoformat()
                            
                            cursor = conn.execute("""
                                UPDATE cursor_sessions
                                SET metadata = ?
                                WHERE external_session_id = ?
                            """, (
                                json.dumps(metadata),
                                external_session_id
                            ))
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse metadata for session {external_session_id}")
                    
                    conn.commit()
                    logger.info(f"Persisted Cursor session end: {external_session_id} (reason: {end_reason})")

        except Exception as e:
            logger.error(f"Failed to persist session end for {external_session_id}: {e}", exc_info=True)
            # Don't raise - allow cleanup to continue

    async def get_session_by_external_id(self, external_session_id: str) -> Optional[dict]:
        """
        Get Cursor session by external session ID.

        Args:
            external_session_id: External session ID from Cursor extension

        Returns:
            Session info dict or None if not found
        """
        try:
            with self.sqlite_client.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT
                        id, external_session_id, workspace_hash,
                        workspace_name, workspace_path, started_at, ended_at, metadata
                    FROM cursor_sessions
                    WHERE external_session_id = ?
                """, (external_session_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                try:
                    metadata = json.loads(row[7]) if row[7] else {}
                except json.JSONDecodeError:
                    metadata = {}
                
                return {
                    'id': row[0],
                    'external_session_id': row[1],
                    'workspace_hash': row[2],
                    'workspace_name': row[3] or '',
                    'workspace_path': row[4] or '',
                    'started_at': row[5],
                    'ended_at': row[6],
                    'metadata': metadata,
                }
        except Exception as e:
            logger.error(f"Failed to get session info for {external_session_id}: {e}", exc_info=True)
            return None

    async def get_internal_session_id(self, external_session_id: str) -> Optional[str]:
        """
        Get internal session ID for external session ID.

        Args:
            external_session_id: External session ID from Cursor extension

        Returns:
            Internal session ID (UUID) or None if not found
        """
        try:
            with self.sqlite_client.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT id FROM cursor_sessions
                    WHERE external_session_id = ?
                """, (external_session_id,))
                
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Failed to get internal session ID for {external_session_id}: {e}", exc_info=True)
            return None

    async def recover_active_sessions(self) -> Dict[str, dict]:
        """
        Query database for Cursor sessions without ended_at.
        
        Called on server startup to restore state.

        Returns:
            Dictionary of external_session_id -> session_info
        """
        try:
            with self.sqlite_client.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT
                        id, external_session_id, workspace_hash,
                        workspace_name, workspace_path, started_at, metadata
                    FROM cursor_sessions
                    WHERE ended_at IS NULL
                    ORDER BY started_at DESC
                """)
                
                rows = cursor.fetchall()
                recovered = {}
                
                for row in rows:
                    external_session_id = row[1]
                    try:
                        metadata = json.loads(row[6]) if row[6] else {}
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse metadata for recovered session {external_session_id}")
                        metadata = {}
                    
                    recovered[external_session_id] = {
                        "session_id": row[0],  # internal session ID
                        "external_session_id": external_session_id,
                        "workspace_hash": row[2],
                        "workspace_name": row[3] or '',
                        "workspace_path": row[4] or '',
                        "platform": "cursor",
                        "started_at": row[5],
                        "source": metadata.get('source', 'recovered'),
                        "recovered": True,
                    }
                
                logger.info(f"Recovered {len(recovered)} active Cursor sessions from database")
                return recovered

        except Exception as e:
            logger.error(f"Failed to recover active sessions: {e}", exc_info=True)
            return {}

    async def mark_session_timeout(
        self,
        external_session_id: str,
        last_activity: datetime
    ) -> None:
        """
        Mark abandoned Cursor session as timed out.
        
        Called by cleanup task for stale sessions.

        Args:
            external_session_id: External session ID from Cursor extension
            last_activity: Last known activity timestamp
        """
        try:
            await self.save_session_end(external_session_id, end_reason='timeout')
            logger.info(f"Marked Cursor session {external_session_id} as timed out (last activity: {last_activity})")
        except Exception as e:
            logger.error(f"Failed to mark Cursor session timeout for {external_session_id}: {e}", exc_info=True)

