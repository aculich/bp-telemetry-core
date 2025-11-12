# Notion Content for BP Experimental Teamspace

This document contains all content needed to create Notion pages. Use this when Notion MCP is configured or to create pages manually.

---

## 1. Teamspace Home Summary

**Page Title**: BP Telemetry Experimental - Project Overview

**Parent**: Teamspace Home for BPExperimental

**Content**:

# BP Telemetry Experimental - Project Overview

## Repository Information
- **GitHub Fork**: [aculich/bp-telemetry-experimental](https://github.com/aculich/bp-telemetry-experimental)
- **Upstream**: [blueplane-ai/bp-telemetry-core](https://github.com/blueplane-ai/bp-telemetry-core)
- **Purpose**: Experimental fork for health monitoring and packaging work
- **Fork Strategy**: Day-based branching (day-0, day-1, day-2+) to maintain Ben's critical path

## Current Status

### Active Work: Day-1 Branch
- **Branch**: `day-1/monitoring-packaging`
- **Worktree**: `experiment/core-monitoring-packaging`
- **Focus**: Health monitoring layer and packaging exploration
- **Key Documents**: 
  - [TODO.md](https://github.com/aculich/bp-telemetry-experimental/blob/day-1/monitoring-packaging/TODO.md) - Implementation plan
  - [UPDATE.md](https://github.com/aculich/bp-telemetry-experimental/blob/day-1/monitoring-packaging/UPDATE.md) - Meeting notes with Ben
  - [WORKTREE_MANAGEMENT.md](https://github.com/aculich/bp-telemetry-experimental/blob/main/WORKTREE_MANAGEMENT.md) - Git workflow guide

### System Context (from Ben's Update)
- **Current State**: Claude and Cursor hooks/traces ingesting into `raw_traces` DB table
- **Components**: 
  - User-level hooks (Claude Code, Cursor)
  - Cursor extension managing sessions
  - Redis worker queue
  - Simple Python server writing to SQLite
- **Current Ingestion**: Async process pulls from Cursor's workspace-level SQLite into own DB
- **Future Simplification**: File watcher may be removed in favor of hook-triggered ingest at end-of-turn

### Key Monitoring Need
- **Chain of custody visibility**: Things getting enqueued to Redis queue successfully → written to database successfully
- **Dead letter queue monitoring**: DLQ is implemented, needs visibility
- **Simple health monitor**: Track messages and system status

## Implementation Phases

### Phase 1: Core Chain of Custody Monitoring (High Priority - Ben's Immediate Need)
1. **Redis Queue Health Monitoring** - See when things are getting enqueued
   - Track enqueue operations
   - Monitor dead letter queue (DLQ is implemented, needs visibility)
   - [GitHub Issue #1](https://github.com/aculich/bp-telemetry-experimental/issues/1)

2. **Database Write Health Monitoring** - Worker processing to write to database
   - Track write success/failure
   - Chain of custody: enqueued → written
   - [GitHub Issue #2](https://github.com/aculich/bp-telemetry-experimental/issues/2)

3. **Unified Health Service** - Chain of Custody Endpoint
   - Simple health monitor
   - Chain of custody visibility endpoint
   - [GitHub Issue #3](https://github.com/aculich/bp-telemetry-experimental/issues/3)

### Phase 2: Capture Health Monitoring (Medium Priority)
4. **Cursor Hook and Capture Health** - Focus on Cursor (not Claude)
   - Monitor Cursor hook execution
   - Monitor Cursor database monitor (async process from workspace SQLite)
   - [GitHub Issue #4](https://github.com/aculich/bp-telemetry-experimental/issues/4)

5. **Health Metrics Storage** - Simple Redis storage
   - [GitHub Issue #5](https://github.com/aculich/bp-telemetry-experimental/issues/5)

### Phase 3: Packaging Research (Medium Priority)
6. **Packaging Strategy Research** - [GitHub Issue #6](https://github.com/aculich/bp-telemetry-experimental/issues/6)
7. **Package Structure Improvements** - [GitHub Issue #7](https://github.com/aculich/bp-telemetry-experimental/issues/7)
8. **Installation Scripts** - [GitHub Issue #8](https://github.com/aculich/bp-telemetry-experimental/issues/8)

### Phase 4: Distribution (Lower Priority)
9. **Distribution Artifacts and Documentation** - [GitHub Issue #9](https://github.com/aculich/bp-telemetry-experimental/issues/9)

## Key Requirements (from Ben)

- **Simple health monitor** to track messages and system status
- **Chain of custody visibility**: Enqueued to Redis queue → written to database
- **Dead letter queue monitoring** - DLQ is implemented, needs visibility
- **Focus on Cursor first** - Claude can come later
- **Live database connection** for real-time monitoring

## Links
- [GitHub Repository](https://github.com/aculich/bp-telemetry-experimental)
- [GitHub Issues](https://github.com/aculich/bp-telemetry-experimental/issues)
- [Fork Issues Database](https://www.notion.so/cef69f45336e4f768ccca41f8e3e9b69?v=851a423677e1486f9854e1d9fde2c145&source=copy_link)

---

## 2. Health Monitoring Implementation Plan

**Page Title**: Health Monitoring Implementation Plan

**Parent**: Teamspace Home for BPExperimental

**Content**: (See TODO.md sections 1.1-1.6 - full content below)

### Overview
Simple at-a-glance view of system health with chain of custody tracking (Redis queue → database writes).

### Current State Analysis

**Existing Monitoring:**
- Basic `/health` endpoint in `src/blueplane/server/api.py`
- Backpressure monitoring in `WorkerPoolManager._monitor_backpressure()`

**Gaps Identified:**
1. No visibility into Redis message queue (`telemetry:events`) health
2. No tracking of database write performance/latency
3. No monitoring of hook execution (success/failure rates)
4. No monitoring of trace capture (transcript monitor, database monitor)
5. No aggregated health dashboard/metrics endpoint
6. No historical health metrics storage

### Implementation Components

#### 1.1 Redis Queue Health Monitoring
- Track enqueue operations
- Monitor dead letter queue (PRIORITY)
- Calculate processing and enqueue rates
- Detect stuck consumers

#### 1.2 Database Write Health Monitoring
- Track write success/failure
- Chain of custody tracking (message IDs: queue → database)
- Monitor write latency and throughput

#### 1.3 Cursor Hook and Capture Health Monitoring
- Focus on Cursor (not Claude)
- Monitor hook execution success/failure
- Track database monitor activity

#### 1.4 Unified Health Service
- Simple health monitor
- Chain of custody endpoint: `/api/v1/health/chain`
- Aggregate health from all monitors

#### 1.5 Health Metrics Storage
- Store in Redis (simple key-value initially)
- 1-minute resolution, 7-day retention

---

## 3. Packaging Exploration Plan

**Page Title**: Packaging Exploration Plan

**Parent**: Teamspace Home for BPExperimental

**Content**: (See TODO.md sections 2.1-2.7)

### Overview
Research and implement distribution strategy for blueplane-telemetry-core.

### Packaging Options to Explore

1. **PyPI Distribution** - Public package on PyPI
2. **Local Wheel Distribution** - Build wheels locally
3. **Git-based Installation** - `pip install git+https://...`
4. **Standalone Executable** - PyInstaller/cx_Freeze
5. **Docker Container** - Containerized distribution

### Implementation Areas

- Package structure improvements
- Installation scripts (`blueplane install` CLI command)
- Distribution artifacts (sdist, wheels, Docker)
- Dependency management
- Platform-specific considerations
- Documentation

---

## 4. Meeting Notes - Ben & Aaron (Nov 11, 2025)

**Page Title**: Meeting Notes - Ben & Aaron (Nov 11, 2025)

**Parent**: Teamspace Home for BPExperimental

**Content**: (Full content from UPDATE.md)

### Key Takeaways

- System Architecture Status: Claude and Cursor hooks/traces successfully ingesting
- Health Monitoring Requirements: Chain of custody visibility from queue to database
- Collaboration Strategy: Day-based branching to maintain Ben's momentum
- Product Prioritization: Cursor first, then Claude

### Action Items

- Aaron: Build simple health monitor tracking message enqueueing, processing, and database writes
- Aaron: Implement monitoring visibility for chain of custody from Redis queue to database
- Aaron: Start investigating packaging system requirements
- Ben: Set up live database connection for real-time monitoring

---

## 5. Git Worktree Management Guide

**Page Title**: Git Worktree Management

**Parent**: Teamspace Home for BPExperimental

**Content**: (Full content from WORKTREE_MANAGEMENT.md)

### Repository Structure

- **upstream**: `blueplane-ai/bp-telemetry-core` (original repository)
- **origin**: `aculich/bp-telemetry-experimental` (your experimental fork)

### Branch Organization

- **`main`**: Always mirrors `upstream/main`
- **`day-0/*`**: Historical/archived experimental work
- **`day-1/*`**: Current active experimental work
- **`day-2/*`**: Future experimental work

### Current Worktrees

1. Main repository: `/Users/me/projects/blueplane-project/experiment/core`
2. Monitoring/Packaging: `/Users/me/projects/blueplane-project/experiment/core-monitoring-packaging`

---

## GitHub Issues to Notion Database Mapping

For syncing to "Fork Issues (experimental)" database:

| Issue # | Title | Phase | Labels | GitHub URL |
|---------|-------|-------|--------|------------|
| #1 | Phase 1.1: Redis Queue Health Monitoring | Phase 1 | enhancement, monitoring, phase-1 | https://github.com/aculich/bp-telemetry-experimental/issues/1 |
| #2 | Phase 1.2: Database Write Health Monitoring | Phase 1 | enhancement, monitoring, phase-1 | https://github.com/aculich/bp-telemetry-experimental/issues/2 |
| #3 | Phase 1.3: Unified Health Service with Chain of Custody Endpoint | Phase 1 | enhancement, monitoring, phase-1, api | https://github.com/aculich/bp-telemetry-experimental/issues/3 |
| #4 | Phase 2.1: Cursor Hook and Capture Health Monitoring | Phase 2 | enhancement, monitoring, phase-2, cursor | https://github.com/aculich/bp-telemetry-experimental/issues/4 |
| #5 | Phase 2.2: Health Metrics Storage | Phase 2 | enhancement, monitoring, phase-2 | https://github.com/aculich/bp-telemetry-experimental/issues/5 |
| #6 | Phase 3.1: Packaging Strategy Research | Phase 3 | packaging, research, phase-3 | https://github.com/aculich/bp-telemetry-experimental/issues/6 |
| #7 | Phase 3.2: Package Structure Improvements | Phase 3 | packaging, phase-3 | https://github.com/aculich/bp-telemetry-experimental/issues/7 |
| #8 | Phase 3.3: Installation Scripts | Phase 3 | packaging, cli, phase-3 | https://github.com/aculich/bp-telemetry-experimental/issues/8 |
| #9 | Phase 4: Distribution Artifacts and Documentation | Phase 4 | packaging, documentation, phase-4 | https://github.com/aculich/bp-telemetry-experimental/issues/9 |

### Database Properties Needed

- **Title** (Title) - Issue title
- **Issue Number** (Number) - GitHub issue number
- **Status** (Select) - Open, Closed
- **Phase** (Select) - Phase 1, Phase 2, Phase 3, Phase 4
- **Labels** (Multi-select) - enhancement, monitoring, packaging, etc.
- **GitHub URL** (URL) - Link to issue
- **Description** (Text) - Issue body content
- **Created Date** (Date) - Issue creation date
- **Updated Date** (Date) - Last update date

