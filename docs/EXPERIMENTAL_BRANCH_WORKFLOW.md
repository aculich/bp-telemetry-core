# Experimental Branch Coordination Workflow

This document describes how to coordinate experimental branches across forks when working on distributed features.

## Overview

When working with experimental branches from upstream (like `cursor-trace-db-mapping`), we need a strategy to:
1. Track upstream experimental branches locally
2. Integrate them into our development workflow
3. Keep our fork's `develop` branch in sync with experimental work
4. Coordinate without conflicts

## Branch Types

### Upstream Branches

- **`upstream/main`**: Stable, production-ready code
- **`upstream/cursor-trace-db-mapping`**: Ben's experimental branch for markdown generation
- **`upstream/feature/*`**: Other feature branches

### Our Fork Branches

- **`main`**: Mirror of `upstream/main` (never commit here)
- **`develop`**: Our fork's main development branch
- **`experimental/*`**: Local tracking branches for upstream experimental branches
- **`feature/*`**: Our feature branches

## Workflow: Tracking Upstream Experimental Branches

### Step 1: Fetch and Create Local Tracking Branch

```bash
# Fetch the experimental branch from upstream
git fetch upstream cursor-trace-db-mapping

# Create a local tracking branch (read-only, for reference)
git checkout -b experimental/cursor-trace-db-mapping upstream/cursor-trace-db-mapping

# Or create it without checking out
git branch experimental/cursor-trace-db-mapping upstream/cursor-trace-db-mapping
```

### Step 2: Integrate into Develop

**Option A: Merge (Preserves History)**
```bash
git checkout develop
git merge experimental/cursor-trace-db-mapping --no-edit
# Resolve any conflicts
git push origin develop
```

**Option B: Rebase (Cleaner History)**
```bash
git checkout develop
git rebase experimental/cursor-trace-db-mapping
# Resolve any conflicts
git push origin develop --force-with-lease
```

**Option C: Cherry-pick Specific Commits**
```bash
git checkout develop
git cherry-pick <commit-sha>
```

### Step 3: Keep Experimental Branch Updated

```bash
# When upstream updates the experimental branch
git fetch upstream cursor-trace-db-mapping
git checkout experimental/cursor-trace-db-mapping
git reset --hard upstream/cursor-trace-db-mapping
```

## Recommended Strategy: Mirror + Merge

For coordinating with Ben's experimental branch:

1. **Create a mirror branch** that tracks his experimental branch
2. **Merge it into develop** to bring in his work
3. **Continue development** on develop or feature branches

```bash
# 1. Create tracking branch
git branch experimental/cursor-trace-db-mapping upstream/cursor-trace-db-mapping

# 2. Merge into develop
git checkout develop
git merge experimental/cursor-trace-db-mapping

# 3. Continue working
git checkout -b feature/my-feature
```

## Updating When Upstream Experimental Branch Changes

When Ben pushes updates to `cursor-trace-db-mapping`:

```bash
# 1. Update the tracking branch
git fetch upstream cursor-trace-db-mapping
git checkout experimental/cursor-trace-db-mapping
git reset --hard upstream/cursor-trace-db-mapping

# 2. Merge new changes into develop
git checkout develop
git merge experimental/cursor-trace-db-mapping

# 3. Push updates
git push origin develop
```

## Best Practices

### ✅ DO

- **Track experimental branches locally**: Create `experimental/*` branches for reference
- **Merge into develop**: Bring experimental work into your main development branch
- **Keep tracking branches updated**: Regularly fetch and reset tracking branches
- **Document dependencies**: Note which experimental branches you're building on
- **Communicate**: Let team know when you're integrating experimental branches

### ❌ DON'T

- **Don't commit to tracking branches**: They're read-only mirrors
- **Don't force push tracking branches**: They should match upstream exactly
- **Don't merge main into experimental branches**: Keep them separate
- **Don't lose your work**: Always merge/rebase onto develop, not the other way

## Example: Integrating Ben's cursor-trace-db-mapping Branch

```bash
# 1. Ensure main is synced
git checkout main
./scripts/sync_upstream.sh

# 2. Fetch Ben's experimental branch
git fetch upstream cursor-trace-db-mapping

# 3. Create local tracking branch
git branch experimental/cursor-trace-db-mapping upstream/cursor-trace-db-mapping

# 4. Merge into develop
git checkout develop
git merge experimental/cursor-trace-db-mapping --no-edit

# 5. Resolve conflicts if any (review changes carefully)
# 6. Push to origin
git push origin develop

# 7. Continue development on feature branches
git checkout -b feature/my-feature
```

## Conflict Resolution

If merging experimental branches causes conflicts:

1. **Review conflicts carefully**: Experimental branches may have different approaches
2. **Preserve both approaches if needed**: Consider keeping both implementations
3. **Document decisions**: Update docs explaining integration choices
4. **Test thoroughly**: Experimental code needs extra validation

## Branch Naming Conventions

- `experimental/<upstream-branch-name>`: Local tracking of upstream experimental branches
- `feature/<description>`: Your feature work
- `fix/<description>`: Bug fixes
- `docs/<description>`: Documentation updates

## Related Documentation

- [Fork Sync Workflow](./FORK_SYNC_WORKFLOW.md) - Syncing main with upstream
- [Architecture](./ARCHITECTURE.md) - Project architecture

