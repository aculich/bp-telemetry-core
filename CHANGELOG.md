<!--
Copyright © 2025 Sierra Labs LLC
SPDX-License-Identifier: AGPL-3.0-only
License-Filename: LICENSE
-->

## Unreleased

### Added

- Workspace History Server (`scripts/start_history_server.py`, `WorkspaceHistoryServer`) to run session and Markdown monitors independently of the main ingest server.
- Cursor Markdown monitor wiring to generate per-workspace `.history` Markdown files with global `~/.blueplane/history/<workspace_hash>` as the default output location.
- Optional DuckDB sink (`DuckDBAdapter`) behind `BLUEPLANE_HISTORY_USE_DUCKDB=1`, used to record workspace snapshot metadata without impacting core ingestion.
- Documentation updates:
  - `docs/SQLITE_VS_DUCKDB.md` summarizing SQLite vs DuckDB tradeoffs and a project-specific rubric.
  - ADR `docs/adr/0001-database-stack-sqlite-and-optional-duckdb.md` capturing the decision to keep SQLite as the primary store with DuckDB as an optional analytical sink.


