# Script Testing Guide

Quick guide for testing the Git workflow management scripts.

## Available Scripts

1. **`sync_upstream.sh`** - Sync `main` with upstream
2. **`start_dev_session.sh`** - Start a development session
3. **`end_dev_session.sh`** - End a development session

## Testing `sync_upstream.sh`

### Test 1: Dry-Run Mode

```bash
# Must be on main branch
git checkout main

# Test dry-run (safe, shows what would happen)
./scripts/sync_upstream.sh --dry-run
```

**Expected Output:**
- Shows current state (local, upstream, origin commits)
- Shows commits that would be added/removed
- Shows what commands would run
- **Does NOT make any changes**

### Test 2: Actual Sync (if needed)

```bash
# Only run if main is actually out of sync
git checkout main
./scripts/sync_upstream.sh
```

**Expected Behavior:**
- Fetches from upstream
- Resets main to match upstream/main
- Force pushes to origin/main

## Testing `start_dev_session.sh`

### Test 1: Basic Start (Auto Feature Name)

```bash
# Start from main (script will switch automatically)
git checkout main
./scripts/start_dev_session.sh
```

**Expected Behavior:**
- Switches to main if needed
- Checks sync status (may ask to sync)
- Updates develop with latest from main
- Creates feature branch: `feature/dev-session-{timestamp}`
- Shows status summary

### Test 2: Start with Custom Feature Name

```bash
git checkout main
./scripts/start_dev_session.sh test-feature
```

**Expected Behavior:**
- Same as above, but creates: `feature/test-feature`

### Test 3: Start When Already on Feature Branch

```bash
# Create a test branch first
git checkout develop
git checkout -b feature/test-branch

# Try to start session
./scripts/start_dev_session.sh
```

**Expected Behavior:**
- Switches to main first
- Then proceeds with normal flow

## Testing `end_dev_session.sh`

### Test 1: End with Uncommitted Changes

```bash
# Create a test feature branch
git checkout develop
git checkout -b feature/test-end-session

# Make some changes
echo "# Test" > test_file.md
git add test_file.md

# End session (interactive)
./scripts/end_dev_session.sh
```

**Expected Behavior:**
- Detects uncommitted changes
- Asks if you want to commit
- Asks for commit message
- Commits changes
- Asks if you want to push
- Optionally switches back to develop

### Test 2: End with Auto-Push

```bash
git checkout feature/test-end-session
./scripts/end_dev_session.sh --push
```

**Expected Behavior:**
- Commits changes (if any)
- Automatically pushes without asking

### Test 3: End with No Commit

```bash
git checkout feature/test-end-session
echo "# More changes" >> test_file.md
./scripts/end_dev_session.sh --no-commit
```

**Expected Behavior:**
- Skips committing
- Still offers to push (if there are commits)
- Leaves changes uncommitted

## Complete Workflow Test

### Full Session Test

```bash
# 1. Start session
git checkout main
./scripts/start_dev_session.sh test-workflow

# 2. Make some changes
echo "# Test Workflow" > test_workflow.md
git add test_workflow.md
git commit -m "test: add workflow test file"

# 3. Make more changes (uncommitted)
echo "# More content" >> test_workflow.md

# 4. End session
./scripts/end_dev_session.sh

# 5. Verify
git checkout develop
git branch -a | grep test-workflow
```

**Expected Result:**
- Feature branch created and pushed
- All changes committed
- Branch exists on origin
- Back on develop branch

## Safety Checks

All scripts include safety checks:

### `sync_upstream.sh`
- ✅ Must be on `main` branch
- ✅ No uncommitted changes
- ✅ Upstream remote exists
- ✅ Dry-run mode available

### `start_dev_session.sh`
- ✅ Handles uncommitted changes (stashes)
- ✅ Checks sync status before proceeding
- ✅ Warns if feature branch exists
- ✅ Shows status summary

### `end_dev_session.sh`
- ✅ Warns if on `main` branch
- ✅ Detects uncommitted changes
- ✅ Confirms before committing
- ✅ Confirms before pushing
- ✅ Shows summary

## Troubleshooting Tests

### Script Not Executable

```bash
chmod +x scripts/*.sh
```

### Script Not Found

```bash
# Make sure you're in repo root
cd /path/to/bp-telemetry-experimental
./scripts/sync_upstream.sh --dry-run
```

### Git Errors

```bash
# Check git status
git status

# Check remotes
git remote -v

# Check branches
git branch -a
```

## Next Steps

After testing:

1. **Review script output** - Make sure behavior matches expectations
2. **Test edge cases** - Try with various git states
3. **Document issues** - Note any problems or improvements needed
4. **Use in real workflow** - Start using scripts for actual development

## Related Documentation

- [DEV_SESSION_WORKFLOW.md](./DEV_SESSION_WORKFLOW.md) - Complete workflow guide
- [FORK_SYNC_WORKFLOW.md](./FORK_SYNC_WORKFLOW.md) - Fork sync details
- [EXPERIMENTAL_BRANCH_WORKFLOW.md](./EXPERIMENTAL_BRANCH_WORKFLOW.md) - Experimental branch workflow

