#!/usr/bin/env python3
# Copyright © 2025 Sierra Labs LLC
# SPDX-License-Identifier: AGPL-3.0-only
# License-Filename: LICENSE

"""
DuckDB adapter scaffold for Blueplane Telemetry Core.

This module is intentionally minimal and optional:
- It only activates if DuckDB is installed and explicitly enabled.
- It mirrors the core SQLite schema for future OLAP-style aggregation.

For now, the adapter is used as a foundation for future work and does not
participate in the main ingestion/markdown paths by default.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import duckdb  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    duckdb = None  # type: ignore[assignment]


class DuckDBAdapter:
    """
    Minimal DuckDB adapter scaffold.

    Responsibilities (current scope):
    - Initialize a DuckDB database at the given path.
    - Ensure a raw_traces table exists with a schema roughly mirroring SQLite.
    - Provide a hook for future bulk-ingest from SQLite or direct writers.

    This should only be constructed when the feature flag is enabled and
    DuckDB is available.
    """

    def __init__(self, db_path: Path):
        if duckdb is None:
            raise RuntimeError(
                "DuckDBAdapter requires the 'duckdb' package. "
                "Install with `pip install duckdb` and enable the feature flag."
            )

        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initializing DuckDB database at {self.db_path}")
        self._conn = duckdb.connect(str(self.db_path))
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        """
        Create a raw_traces-like table if it does not already exist.

        The schema is intentionally simplified; it mirrors the main identifiers
        and a JSON payload column for future expansion.
        """
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_traces (
                sequence BIGINT,
                ingested_at TIMESTAMP,
                event_id VARCHAR,
                session_id VARCHAR,
                event_type VARCHAR,
                platform VARCHAR,
                timestamp TIMESTAMP,
                workspace_hash VARCHAR,
                model VARCHAR,
                tool_name VARCHAR,
                duration_ms BIGINT,
                tokens_used BIGINT,
                lines_added BIGINT,
                lines_removed BIGINT,
                event_data_json JSON
            )
            """
        )
        logger.info("Ensured DuckDB raw_traces table exists")

    def close(self) -> None:
        """Close the DuckDB connection."""
        try:
            self._conn.close()
        except Exception:
            logger.debug("DuckDB connection already closed or failed to close")


