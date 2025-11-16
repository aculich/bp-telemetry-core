# Development Session Workflow

This document describes the standardized workflow for starting and ending development sessions using the provided scripts.

## Overview

The development session scripts provide a consistent, safe workflow for:
- Starting a new development session
- Ending a development session
- Managing feature branches
- Keeping branches in sync

## Scripts

### `start_dev_session.sh`

Starts a new development session by:
1. Syncing `main` with upstream (with confirmation)
2. Updating `develop` with latest from `main`
3. Creating or checking out a feature branch
4. Showing current status

**Usage:**
```bash
# Auto-generate feature branch name
./scripts/start_dev_session.sh

# Use custom feature name
./scripts/start_dev_session.sh my-feature-name
```

**What it does:**
- Checks you're on `main` (switches if needed)
- Stashes any uncommitted changes on `main`
- Checks if `main` needs syncing (asks for confirmation)
- Updates `develop` with latest from `main`
- Creates feature branch: `feature/{name}` or `feature/dev-session-{timestamp}`
- Shows status summary

**Example:**
```bash
$ ./scripts/start_dev_session.sh cursor-markdown-improvements

🚀 Starting Development Session
================================

📋 Step 1: Syncing main with upstream...
   ✅ main is already in sync with upstream

📋 Step 2: Updating develop branch...
   ✅ Merged latest changes from main into develop

📋 Step 3: Setting up feature branch...
   Using feature branch: feature/cursor-markdown-improvements
   ✅ Created and checked out feature branch: feature/cursor-markdown-improvements

📋 Step 4: Current Status
================================
   Current branch: feature/cursor-markdown-improvements
   Upstream status: ## feature/cursor-markdown-improvements...origin/develop

✅ Development session ready!
```

### `end_dev_session.sh`

Ends a development session by:
1. Checking for uncommitted changes
2. Committing changes (with confirmation)
3. Pushing branch to origin (with confirmation)
4. Optionally switching back to `develop`

**Usage:**
```bash
# Interactive mode (asks for confirmations)
./scripts/end_dev_session.sh

# Auto-push without asking
./scripts/end_dev_session.sh --push

# Skip committing (leave changes uncommitted)
./scripts/end_dev_session.sh --no-commit

# Combine flags
./scripts/end_dev_session.sh --push --no-commit
```

**What it does:**
- Checks current branch (warns if on `main`)
- Detects uncommitted changes
- Offers to commit changes (with custom message)
- Checks if branch needs pushing
- Offers to push to origin
- Optionally switches back to `develop`
- Shows session summary

**Example:**
```bash
$ ./scripts/end_dev_session.sh

🏁 Ending Development Session
================================

📋 Current branch: feature/cursor-markdown-improvements

📋 Step 1: Checking for uncommitted changes...
   ⚠️  You have uncommitted changes:
   M  src/processing/cursor/markdown_writer.py
   A  tests/test_markdown.py
   📝 Enter commit message (or press Enter for default):
   feat: add conversation message loading
   ✅ Changes committed

📋 Step 2: Checking branch status...
   📤 Branch has 1 local commit(s) not pushed
   Push to origin? (Y/n): y
   📤 Pushing to origin...
   ✅ Pushed to origin

📋 Step 3: Session Summary
================================
   Branch: feature/cursor-markdown-improvements
   Status: ## feature/cursor-markdown-improvements...origin/feature/cursor-markdown-improvements [ahead 1]

📋 Step 4: Cleanup
   Switch back to develop branch? (y/N): y
   ✅ Switched to develop branch

✅ Development session ended!
```

## Complete Workflow Example

### Starting a Session

```bash
# 1. Start development session
./scripts/start_dev_session.sh implement-global-storage

# 2. Make your changes
vim src/processing/cursor/markdown_writer.py
# ... edit files ...

# 3. Test your changes
python -m pytest tests/

# 4. Commit as you go
git add .
git commit -m "feat: add global storage query support"
```

### Ending a Session

```bash
# 1. End development session (interactive)
./scripts/end_dev_session.sh

# Or end with auto-push
./scripts/end_dev_session.sh --push
```

## Best Practices

### ✅ DO

- **Use feature branches**: Always work on feature branches, never directly on `develop` or `main`
- **Start sessions properly**: Use `start_dev_session.sh` to ensure branches are synced
- **Commit frequently**: Commit logical units of work
- **End sessions cleanly**: Use `end_dev_session.sh` to ensure nothing is lost
- **Push regularly**: Push your feature branch to origin for backup

### ❌ DON'T

- **Don't skip sync**: Always sync `main` before starting work
- **Don't work on main**: Never commit directly to `main`
- **Don't leave uncommitted work**: Commit or stash before ending session
- **Don't forget to push**: Push feature branches to origin for safety

## Integration with Other Scripts

### With `sync_upstream.sh`

```bash
# Start session (syncs main automatically)
./scripts/start_dev_session.sh my-feature

# ... work ...

# End session
./scripts/end_dev_session.sh
```

### Manual Workflow

If you prefer manual control:

```bash
# 1. Sync main
git checkout main
./scripts/sync_upstream.sh

# 2. Update develop
git checkout develop
git merge main

# 3. Create feature branch
git checkout -b feature/my-feature

# 4. Work...

# 5. Commit and push
git add .
git commit -m "feat: my changes"
git push origin feature/my-feature

# 6. Switch back to develop
git checkout develop
```

## Troubleshooting

### "Must be on main branch"

**Problem**: `start_dev_session.sh` requires you to be on `main` initially.

**Solution**: The script will automatically switch to `main` if you're on another branch.

### "You have uncommitted changes"

**Problem**: Script detects uncommitted changes.

**Solution**: 
- `start_dev_session.sh`: Automatically stashes changes on `main`
- `end_dev_session.sh`: Offers to commit changes

### "Branch already exists"

**Problem**: Feature branch name already exists.

**Solution**: 
- Choose a different name
- Or checkout the existing branch if you want to continue work

### "Push failed"

**Problem**: Cannot push to origin.

**Solution**:
- Check git remote: `git remote -v`
- Check authentication: `git push origin HEAD --dry-run`
- Verify branch name doesn't conflict

## Related Documentation

- [Fork Sync Workflow](./FORK_SYNC_WORKFLOW.md) - Syncing main with upstream
- [Experimental Branch Workflow](./EXPERIMENTAL_BRANCH_WORKFLOW.md) - Working with experimental branches
- [STARTHERE.md](../STARTHERE.md) - Developer's guide

