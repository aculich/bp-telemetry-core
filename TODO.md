# TODO: Health Monitoring & Packaging

Based on Ben's request and codebase analysis, this document outlines the tasks for implementing health monitoring and exploring packaging approaches.

## Overview

This work focuses on two main areas:
1. **Health Monitoring Layer**: Simple at-a-glance view of system health with chain of custody tracking (Redis queue → database writes)
2. **Packaging Exploration**: Research and implement distribution strategy

## Product Requirements

- **Health monitor with chain of custody visibility**: Track messages from Redis queue enqueue → database write success
- **Real-time monitoring of Redis queue operations**: See when things are getting enqueued and moving through
- **Database write success/failure tracking**: Monitor worker processing to write to the database
- **Dead letter queue monitoring integration**: Dead letter queue is implemented, needs visibility
- **Live database connection implementation**: Dependency on live database connection for real-time monitoring
- **Packaging system for distribution**: Start looking at packaging the system
- **Telemetry visualization interfaces** (future): Foundation for future visualization tools

## User Stories

- **As a developer**, I want to see when messages are enqueued to Redis so that I can verify the ingestion pipeline is working
- **As a system administrator**, I want to monitor the chain of custody from queue to database so that I can identify failure points
- **As a developer**, I want visibility into dead letter queue activity so that I can troubleshoot failed message processing
- **As a user**, I want the system to trigger ingests from hooks at end-of-turn so that I get real-time trace collection
- **As a developer**, I want live database connections so that I can monitor system health in real-time

## Objectives and Goals

- Implement comprehensive health monitoring for telemetry pipeline
- Establish reliable chain of custody tracking from ingestion to storage
- Create packaging system for distribution
- Maintain development momentum while enabling collaborative contribution
- **Prioritize Cursor implementation** as foundation for Claude features (Cursor focus first)
- Build robust observability infrastructure for future visualization tools

## System Context (Ben's Update)

**Current System State:**
- Claude and Cursor hooks/traces are ingested into a `raw_traces` DB table
- Components: user-level hooks, Cursor extension managing sessions, Redis worker queue, simple Python server writing to SQLite
- Current ingestion: async process pulls from Cursor's workspace-level SQLite into own DB
- **File watcher exists but may be removed** in favor of hook-triggered ingest at end-of-turn

**Key Monitoring Need:**
- See chain of custody: things getting enqueued to Redis queue successfully → written to database successfully
- Dead letter queue is implemented, needs visibility
- Simple health monitor to track messages and system status

---

## Part 1: Health Monitoring Layer

### Current State Analysis

**Existing Monitoring:**
- Basic `/health` endpoint in `src/blueplane/server/api.py` (lines 383-402)
  - Checks database connection (SQLite)
  - Checks Redis connection
  - Returns simple healthy/unhealthy status
- Backpressure monitoring in `WorkerPoolManager._monitor_backpressure()` (lines 146-181)
  - Monitors CDC queue depth
  - Logs warnings at thresholds (10k, 50k, 100k)
  - No metrics exposed or persisted

**Gaps Identified:**
1. No visibility into Redis message queue (`telemetry:events`) health
2. No tracking of database write performance/latency
3. No monitoring of hook execution (success/failure rates)
4. No monitoring of trace capture (transcript monitor, database monitor)
5. No aggregated health dashboard/metrics endpoint
6. No historical health metrics storage

### 1.1 Redis Message Queue Health Monitoring

**Location**: `src/blueplane/monitoring/queue_health.py` (new file)

**Requirements (from Ben's request):**
- **See when things are getting enqueued to that queue** - Track enqueue operations
- **When they're moving through** - Monitor processing flow
- **Dead letter queue monitoring** - Dead letter queue is implemented, needs visibility
- Track queue depth and consumer lag
- Calculate processing rate (events/second)
- Detect stuck consumers

**Metrics to Track:**
```python
{
    "queue_depth": int,              # Current stream length (telemetry:events)
    "pending_messages": int,         # Unprocessed messages in PEL
    "oldest_pending_age_ms": int,     # Age of oldest pending message
    "consumer_count": int,            # Active consumers in group
    "processing_rate_events_per_sec": float,
    "dlq_size": int,                 # Dead letter queue size (telemetry:dlq) - PRIORITY
    "dlq_recent_entries": int,        # Entries added to DLQ in last hour
    "enqueue_rate_events_per_sec": float,  # Rate of messages being enqueued
    "consumer_lag_ms": int,           # Time since last processed message
    "health_status": "green|yellow|orange|red"
}
```

**Implementation Tasks:**
- [ ] Create `QueueHealthMonitor` class
- [ ] Implement Redis Stream info collection (XINFO, XPENDING)
- [ ] **Track enqueue operations** - Monitor XADD to `telemetry:events`
- [ ] **Monitor dead letter queue** - Track `telemetry:dlq` stream size and recent entries
- [ ] Calculate processing rate from stream timestamps
- [ ] Calculate enqueue rate (messages/second being added)
- [ ] Detect stuck consumers (no ACK in >30 seconds)
- [ ] Add health status calculation (green/yellow/orange/red thresholds)
- [ ] Add to health monitoring service

**Thresholds:**
- Green: queue_depth < 1000, pending < 100, lag < 5s, dlq_size = 0
- Yellow: queue_depth 1000-10000, pending 100-1000, lag 5-30s, dlq_size < 10
- Orange: queue_depth 10000-50000, pending 1000-5000, lag 30-60s, dlq_size 10-100
- Red: queue_depth > 50000, pending > 5000, lag > 60s, dlq_size > 100

### 1.2 Database Write Health Monitoring

**Location**: `src/blueplane/monitoring/database_health.py` (new file)

**Requirements (from Ben's request):**
- **Worker processing to write to the database** - Track successful writes
- **Chain of custody**: Messages enqueued → written to database successfully
- **Database write success/failure tracking** - Critical for identifying failure points
- Monitor SQLite write performance and errors
- Track write throughput (events/second)

**Metrics to Track:**
```python
{
    "write_success_count": int,       # Successful writes (chain of custody)
    "write_failure_count": int,       # Failed writes (chain of custody break)
    "write_success_rate": float,      # Success rate (0.0-1.0)
    "write_latency_p95_ms": float,    # P95 latency for writes
    "write_throughput_events_per_sec": float,
    "last_successful_write_timestamp": str,  # Last successful write time
    "last_failed_write_timestamp": str,      # Last failed write time
    "db_size_mb": float,
    "wal_size_mb": float,
    "health_status": "green|yellow|orange|red"
}
```

**Chain of Custody Tracking:**
- Track message IDs from Redis queue → database write
- Identify messages that were enqueued but never written (chain break)
- Correlate DLQ entries with failed database writes

**Implementation Tasks:**
- [ ] Create `DatabaseHealthMonitor` class
- [ ] Instrument `SQLiteBatchWriter.write_batch()` with timing and success/failure tracking
- [ ] **Track chain of custody**: Correlate message IDs from queue to database writes
- [ ] Track write latencies (P95 sufficient for simple monitor)
- [ ] Monitor database file size (periodic checks)
- [ ] Track WAL file size
- [ ] Add error counting and failure tracking
- [ ] Add to health monitoring service

**Thresholds:**
- Green: success_rate > 99%, P95 < 10ms, throughput > 100 events/sec
- Yellow: success_rate 95-99%, P95 10-50ms, throughput 50-100 events/sec
- Orange: success_rate 90-95%, P95 50-100ms, throughput 10-50 events/sec
- Red: success_rate < 90%, P95 > 100ms, throughput < 10 events/sec

### 1.3 Hook and Trace Capture Health Monitoring

**Location**: `src/blueplane/monitoring/capture_health.py` (new file)

**Requirements (from Ben's request):**
- **Focus on Cursor** (not Claude) - Cursor implementation is priority
- Monitor Cursor hook execution and success/failure rates
- Monitor database monitor (Cursor) health - async process pulling from Cursor's workspace SQLite
- Track event capture rate
- **Note**: File watcher exists but may be removed in favor of hook-triggered ingest

**Metrics to Track:**
```python
{
    "cursor_hooks": {
        "total_executions": int,
        "success_count": int,
        "failure_count": int,
        "success_rate": float,
        "last_execution_timestamp": str,
        "hooks_active": {
            "beforeSubmitPrompt": bool,
            "afterAgentResponse": bool,
            "beforeMCPExecution": bool,
            "afterMCPExecution": bool,
            "afterFileEdit": bool,
            "stop": bool
        }
    },
    "database_monitor": {
        "active": bool,
        "sessions_monitored": int,
        "events_captured": int,
        "last_activity_timestamp": str,
        "errors_count": int,
        "ingest_rate_events_per_min": float  # From Cursor workspace SQLite
    },
    "capture_rate_events_per_min": float,  # Overall capture rate
    "health_status": "green|yellow|orange|red"
}
```

**Implementation Tasks:**
- [ ] Create `CaptureHealthMonitor` class
- [ ] **Focus on Cursor hooks** - Add hook execution tracking to `MessageQueueWriter.enqueue()`
  - Track success/failure per Cursor hook type
  - Track last execution timestamp
- [ ] **Monitor Cursor database monitor** - Track `CursorDatabaseMonitor` activity
  - Monitor async process pulling from Cursor's workspace SQLite
  - Track sessions monitored and events captured
  - Track ingest rate
- [ ] Calculate capture rate from recent events
- [ ] Detect inactive hooks (no events in >5 minutes)
- [ ] Add to health monitoring service
- [ ] **Note**: Claude hooks can be added later (lower priority)

**Thresholds:**
- Green: success_rate > 99%, capture_rate > 10 events/min, database monitor active
- Yellow: success_rate 95-99%, capture_rate 5-10 events/min, database monitor intermittent
- Orange: success_rate 90-95%, capture_rate 1-5 events/min, database monitor inactive
- Red: success_rate < 90%, capture_rate < 1 events/min, database monitor down

### 1.4 Unified Health Monitoring Service

**Location**: `src/blueplane/monitoring/health_service.py` (new file)

**Requirements (from Ben's request):**
- **Simple health monitor** to track messages and system status
- **Chain of custody visibility**: Enqueued to Redis queue successfully → written to database successfully
- **At-a-glance status** - Simple, not complex
- Provide live database connection for real-time monitoring
- Expose health metrics via API

**API Endpoints:**
- `GET /api/v1/health` - Overall system health (enhanced with chain of custody)
- `GET /api/v1/health/queue` - Queue-specific health (enqueue rate, DLQ)
- `GET /api/v1/health/database` - Database-specific health (write success/failure)
- `GET /api/v1/health/capture` - Capture-specific health (Cursor hooks, database monitor)
- `GET /api/v1/health/chain` - **Chain of custody endpoint** - Messages enqueued → written

**Chain of Custody Endpoint Response:**
```python
{
    "chain_status": "healthy|degraded|broken",
    "messages_enqueued_last_hour": int,
    "messages_written_last_hour": int,
    "messages_in_dlq": int,
    "chain_break_count": int,  # Enqueued but not written
    "last_chain_break_timestamp": str,
    "success_rate": float  # Written / Enqueued
}
```

**Implementation Tasks:**
- [ ] Create `HealthService` class
- [ ] Integrate `QueueHealthMonitor`, `DatabaseHealthMonitor`, `CaptureHealthMonitor`
- [ ] **Implement chain of custody tracking** - Correlate enqueued messages with database writes
- [ ] Calculate overall health status (worst of all components)
- [ ] Store health metrics in Redis (simple key-value, not necessarily TimeSeries initially)
- [ ] Create FastAPI endpoints for health data
- [ ] Add health metrics to existing `/health` endpoint
- [ ] **Create chain of custody endpoint** (`/api/v1/health/chain`)

**Health Status Calculation:**
```python
overall_status = max(
    queue_health.status,
    database_health.status,
    capture_health.status
)
# green=0, yellow=1, orange=2, red=3
```

### 1.5 Health Metrics Storage

**Location**: `src/blueplane/monitoring/health_storage.py` (new file)

**Requirements:**
- Store health metrics in Redis TimeSeries
- 1-minute resolution, 7-day retention
- Enable historical analysis
- Support health trend visualization

**Implementation Tasks:**
- [ ] Create `HealthMetricsStorage` class
- [ ] Use Redis TimeSeries for metrics storage
- [ ] Store metrics: queue_depth, write_latency_p95, capture_rate, etc.
- [ ] Implement retention policy (7 days)
- [ ] Add query methods for historical data

### 1.6 Integration Points

**Files to Modify:**
- `src/blueplane/server/api.py` - Add health endpoints
- `src/blueplane/fast_path/writer.py` - Add write latency tracking
- `src/blueplane/capture/queue_writer.py` - Add hook execution tracking
- `src/blueplane/capture/transcript_monitor.py` - Add activity tracking
- `src/blueplane/capture/database_monitor.py` - Add activity tracking
- `scripts/run_server.py` - Start health monitoring service

---

## Part 2: Packaging Exploration

### Current State Analysis

**Existing Packaging:**
- `pyproject.toml` configured with hatchling build backend
- Package name: `blueplane-telemetry-core`
- Version: `0.1.0`
- Entry point: `blueplane = blueplane.cli.main:main`
- Dependencies specified
- Optional dev dependencies

**Gaps Identified:**
1. No distribution strategy (PyPI, local wheels, etc.)
2. No installation documentation
3. No hook installation as part of package install
4. No systemd/service files for server
5. No Docker containerization
6. No dependency on Redis/SQLite (assumed installed)
7. No post-install scripts

### 2.1 Packaging Strategy Research

**Options to Explore:**

1. **PyPI Distribution**
   - Public package on PyPI
   - `pip install blueplane-telemetry-core`
   - Pros: Standard, easy installation
   - Cons: Requires public release, versioning strategy

2. **Local Wheel Distribution**
   - Build wheels locally
   - Install via `pip install wheel_file.whl`
   - Pros: Private, version control
   - Cons: Manual distribution

3. **Git-based Installation**
   - `pip install git+https://...`
   - Pros: Always latest, version control
   - Cons: Requires git access, build on install

4. **Standalone Executable**
   - PyInstaller/cx_Freeze
   - Single binary distribution
   - Pros: No Python version dependency
   - Cons: Larger size, platform-specific

5. **Docker Container**
   - Containerized distribution
   - Includes Redis, SQLite
   - Pros: Self-contained, reproducible
   - Cons: Docker dependency

**Research Tasks:**
- [ ] Evaluate each option for this use case
- [ ] Document pros/cons for each
- [ ] Recommend primary and secondary approaches
- [ ] Consider hybrid approach (PyPI + Docker)

### 2.2 Package Structure Improvements

**Current Structure:**
```
blueplane-telemetry-core/
├── src/blueplane/
├── hooks/
├── scripts/
├── tests/
└── pyproject.toml
```

**Improvements Needed:**
- [ ] Ensure all necessary files included in package
- [ ] Add hook scripts to package data
- [ ] Add configuration templates
- [ ] Add service files (systemd, launchd)
- [ ] Add installation scripts

**Tasks:**
- [ ] Review `pyproject.toml` package configuration
- [ ] Add `[tool.hatch.build.targets.wheel.shared-data]` for hooks
- [ ] Add `[tool.hatch.build.targets.wheel.scripts]` for additional scripts
- [ ] Create `MANIFEST.in` if needed for extra files
- [ ] Test package build: `python -m build`

### 2.3 Installation Scripts

**Location**: `src/blueplane/cli/install.py` (new command)

**Requirements:**
- Post-install hook installation
- Redis check/configuration
- Database initialization
- Service setup (optional)

**Tasks:**
- [ ] Create `blueplane install` CLI command
- [ ] Integrate hook installation (`install_hooks.py` logic)
- [ ] Add Redis connectivity check
- [ ] Add database initialization
- [ ] Add service file installation (systemd/launchd)
- [ ] Add verification step

### 2.4 Distribution Artifacts

**Artifacts to Create:**
- [ ] Source distribution (sdist)
- [ ] Wheel distribution (wheel)
- [ ] Docker image (if chosen)
- [ ] Installation documentation
- [ ] Quick start guide

**Tasks:**
- [ ] Set up build process (`python -m build`)
- [ ] Create `.github/workflows/build.yml` for CI/CD
- [ ] Document build process
- [ ] Test installation from each artifact type

### 2.5 Dependency Management

**Current Dependencies:**
- Redis (external)
- SQLite (built-in Python)
- Python 3.11+

**Considerations:**
- [ ] Document Redis installation requirements
- [ ] Consider bundling Redis (Docker only)
- [ ] Document Python version requirements
- [ ] Consider optional dependencies (e.g., dashboard)

**Tasks:**
- [ ] Update `pyproject.toml` with optional dependencies
- [ ] Create `requirements.txt` for easy install
- [ ] Document external dependencies
- [ ] Add dependency check script

### 2.6 Platform-Specific Considerations

**Platforms:**
- macOS (Darwin)
- Linux
- Windows (if supported)

**Tasks:**
- [ ] Test package build on each platform
- [ ] Document platform-specific installation
- [ ] Handle platform-specific service files
- [ ] Test hook installation on each platform

### 2.7 Documentation

**Documentation Needed:**
- [ ] Installation guide
- [ ] Packaging strategy document
- [ ] Distribution process
- [ ] Versioning strategy
- [ ] Release process

**Tasks:**
- [ ] Create `docs/PACKAGING.md`
- [ ] Create `docs/INSTALLATION.md`
- [ ] Update `README.md` with installation instructions
- [ ] Document versioning approach (semver?)

---

## Implementation Priority

### Phase 1: Core Chain of Custody Monitoring (High Priority - Ben's Immediate Need)
1. **Redis Queue Health Monitoring (1.1)** - See when things are getting enqueued
   - Track enqueue operations
   - Monitor dead letter queue (DLQ is implemented, needs visibility)
2. **Database Write Health Monitoring (1.2)** - Worker processing to write to database
   - Track write success/failure
   - Chain of custody: enqueued → written
3. **Unified Health Service (1.4) - Chain of Custody Endpoint**
   - Simple health monitor
   - Chain of custody visibility endpoint

### Phase 2: Capture Health Monitoring (Medium Priority)
4. **Cursor Hook and Capture Health (1.3)** - Focus on Cursor (not Claude)
   - Monitor Cursor hook execution
   - Monitor Cursor database monitor (async process from workspace SQLite)
5. Health Metrics Storage (1.5) - Simple Redis storage
6. Enhanced Health Service (1.4) - Full version with all endpoints

### Phase 3: Packaging Research (Medium Priority)
7. Packaging Strategy Research (2.1)
8. Package Structure Improvements (2.2)
9. Installation Scripts (2.3)

### Phase 4: Distribution (Lower Priority)
10. Distribution Artifacts (2.4)
11. Dependency Management (2.5)
12. Platform-Specific Considerations (2.6)
13. Documentation (2.7)

---

## Notes

- **Keep it simple** - Ben requested a "simple health monitor", not an enterprise monitoring solution
- Health monitoring should be lightweight and not impact performance
- **Chain of custody is the key requirement** - Track messages from Redis queue → database write
- **Dead letter queue monitoring is critical** - DLQ is implemented, needs visibility
- **Focus on Cursor first** - Claude can come later (Ben's prioritization)
- Consider using Redis for health metrics storage (already in use)
- Health endpoints should be fast (<10ms response time)
- **Live database connection** - Dependency for real-time monitoring
- Packaging should support both development and production use cases
- Consider backward compatibility when changing package structure

---

## References

- Current health check: `src/blueplane/server/api.py:383-402`
- Backpressure monitoring: `src/blueplane/slow_path/worker_pool.py:146-181`
- Package config: `pyproject.toml`
- Hook installation: `scripts/install_hooks.py`
- Architecture docs: `docs/architecture/`

