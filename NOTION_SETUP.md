# Notion Setup Guide

This document provides content and structure for creating Notion pages based on the project documentation.

## GitHub Issues Created

9 issues have been created in https://github.com/aculich/bp-telemetry-experimental/issues:

1. **#1** - Phase 1.1: Redis Queue Health Monitoring
2. **#2** - Phase 1.2: Database Write Health Monitoring  
3. **#3** - Phase 1.3: Unified Health Service with Chain of Custody Endpoint
4. **#4** - Phase 2.1: Cursor Hook and Capture Health Monitoring
5. **#5** - Phase 2.2: Health Metrics Storage
6. **#6** - Phase 3.1: Packaging Strategy Research
7. **#7** - Phase 3.2: Package Structure Improvements
8. **#8** - Phase 3.3: Installation Scripts
9. **#9** - Phase 4: Distribution Artifacts and Documentation

## Notion Pages to Create

### 1. Teamspace Home Summary

**Page Title**: BP Experimental - Project Overview

**Content**:

# BP Telemetry Experimental - Project Overview

## Repository
- **GitHub**: https://github.com/aculich/bp-telemetry-experimental
- **Forked from**: https://github.com/blueplane-ai/bp-telemetry-core
- **Purpose**: Experimental fork for health monitoring and packaging work

## Current Status

### Day-1 Work (Active)
- **Branch**: `day-1/monitoring-packaging`
- **Focus**: Health monitoring layer and packaging exploration
- **Key Documents**: 
  - TODO.md - Implementation plan
  - UPDATE.md - Meeting notes with Ben
  - WORKTREE_MANAGEMENT.md - Git workflow guide

### System Context
- **Current State**: Claude and Cursor hooks/traces ingesting into `raw_traces` DB table
- **Components**: User-level hooks, Cursor extension, Redis worker queue, Python server writing to SQLite
- **Key Need**: Chain of custody visibility (Redis queue → database writes)

## Implementation Phases

### Phase 1: Core Chain of Custody Monitoring (High Priority)
1. Redis Queue Health Monitoring
2. Database Write Health Monitoring
3. Unified Health Service with Chain of Custody Endpoint

### Phase 2: Capture Health Monitoring (Medium Priority)
4. Cursor Hook and Capture Health Monitoring
5. Health Metrics Storage

### Phase 3: Packaging Research (Medium Priority)
6. Packaging Strategy Research
7. Package Structure Improvements
8. Installation Scripts

### Phase 4: Distribution (Lower Priority)
9. Distribution Artifacts and Documentation

## Key Requirements (from Ben)

- **Simple health monitor** to track messages and system status
- **Chain of custody visibility**: Enqueued to Redis queue → written to database
- **Dead letter queue monitoring** - DLQ is implemented, needs visibility
- **Focus on Cursor first** - Claude can come later
- **Live database connection** for real-time monitoring

## Links
- [GitHub Issues](https://github.com/aculich/bp-telemetry-experimental/issues)
- [Fork Issues (experimental)](https://www.notion.so/cef69f45336e4f768ccca41f8e3e9b69?v=851a423677e1486f9854e1d9fde2c145&source=copy_link)

---

### 2. Health Monitoring Implementation Plan

**Page Title**: Health Monitoring Implementation Plan

**Content**: Copy from TODO.md sections 1.1-1.6

---

### 3. Packaging Exploration Plan

**Page Title**: Packaging Exploration Plan

**Content**: Copy from TODO.md sections 2.1-2.7

---

### 4. Meeting Notes and Requirements

**Page Title**: Meeting Notes - Ben & Aaron (Nov 11, 2025)

**Content**: Copy from UPDATE.md

---

### 5. Worktree Management Guide

**Page Title**: Git Worktree Management

**Content**: Copy from WORKTREE_MANAGEMENT.md

---

## Notion Database Setup for GitHub Issues Sync

To sync GitHub issues to Notion database "Fork Issues (experimental)":

1. **Database Properties Needed**:
   - Title (Title)
   - Issue Number (Number)
   - Status (Select: Open, Closed)
   - Phase (Select: Phase 1, Phase 2, Phase 3, Phase 4)
   - Labels (Multi-select)
   - GitHub URL (URL)
   - Description (Text)
   - Created Date (Date)
   - Updated Date (Date)

2. **Issue Mapping**:
   - Issue #1 → Phase 1.1: Redis Queue Health Monitoring
   - Issue #2 → Phase 1.2: Database Write Health Monitoring
   - Issue #3 → Phase 1.3: Unified Health Service
   - Issue #4 → Phase 2.1: Cursor Hook and Capture Health
   - Issue #5 → Phase 2.2: Health Metrics Storage
   - Issue #6 → Phase 3.1: Packaging Strategy Research
   - Issue #7 → Phase 3.2: Package Structure Improvements
   - Issue #8 → Phase 3.3: Installation Scripts
   - Issue #9 → Phase 4: Distribution Artifacts

## Next Steps

1. Create Notion pages using the content above
2. Set up GitHub → Notion sync (may require Notion MCP configuration)
3. Link issues to implementation tasks
4. Track progress in Notion database

