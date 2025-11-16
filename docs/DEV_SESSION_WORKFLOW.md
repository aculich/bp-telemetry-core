# Development Session Workflow

This document describes the standardized workflow for starting and ending development sessions using the provided scripts.

## Overview

The development session scripts provide a consistent, safe workflow for:
- Starting a new development session
- Ending a development session
- Managing feature branches
- Keeping branches in sync

## Scripts

### `resume_dev_session.sh`

Resumes a recent development session by checking out a session branch that has commits.

**Usage:**
```bash
./scripts/resume_dev_session.sh
```

**What it does:**
- Lists recent `dev/session-*` branches (sorted by date)
- Filters out empty sessions (branches with no commits)
- Shows branch name, date, and relative time
- Defaults to most recent session (just press Enter)
- Allows selecting any branch from the list
- Handles uncommitted changes (offers to stash)
- Creates local tracking branch if only exists on remote

**Example:**
```bash
$ ./scripts/resume_dev_session.sh

🔄 Resuming Development Session
================================

📋 Recent development sessions (with commits):

   [1] dev/session-20251115-200000 [default]
       2025-11-15 (2 hours ago)
   [2] dev/session-20251115-182135
       2025-11-15 (4 hours ago)

Select session to resume (1-2) [default: 1]: 
📋 Resuming session: dev/session-20251115-200000
   ✅ Checked out branch: dev/session-20251115-200000

✅ Session resumed!
```

### `start_dev_session.sh`

Starts a new development session by:
1. Syncing `main` with upstream (with confirmation)
2. Updating `develop` with latest from `main`
3. Creating or checking out a feature branch (if provided)
4. Creating a session branch from the feature branch (or develop)
5. Showing current status

**Usage:**
```bash
# Session from develop (auto-generated session name)
./scripts/start_dev_session.sh

# Session from feature branch (auto-generated session name)
./scripts/start_dev_session.sh my-feature

# Named session from feature branch
./scripts/start_dev_session.sh my-feature session-name

# Tab completion for feature branches (add to ~/.zshrc):
#   source /path/to/scripts/_start_dev_session_completion.sh
```

**What it does:**
- Checks you're on `main` (switches if needed)
- Stashes any uncommitted changes on `main`
- Checks if `main` needs syncing (asks for confirmation)
- Updates `develop` with latest from `main`
- If feature branch provided: creates/checks out `feature/{name}`
- Creates session branch: `dev/session-{timestamp}` from feature branch (or develop)
- Stores base branch in git config for proper merge target
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
   Feature branch: feature/cursor-markdown-improvements
   ✅ Feature branch exists, checking out...

📋 Step 4: Setting up development session branch...
   No session name provided, using: dev/session-20251115-200000
   ✅ Created and checked out session branch: dev/session-20251115-200000
   📌 Session will merge back into: feature/cursor-markdown-improvements

📋 Step 5: Current Status
================================
   Current branch: dev/session-20251115-200000
   Upstream status: ## dev/session-20251115-200000

✅ Development session ready!

Feature branch: feature/cursor-markdown-improvements
Session branch: dev/session-20251115-200000
```

### `end_dev_session.sh`

Ends a development session by:
1. Checking for uncommitted changes and untracked files
2. Handling junk files (ignore/leave alone/commit/abort)
3. Committing changes (with confirmation and file list)
4. Pushing branch to origin (with confirmation)
5. Merging session branch into base branch (feature or develop)
6. Switching back to base branch

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
- Detects uncommitted changes and untracked files
- Uses AI (llm) to classify files (junk vs. important)
- Offers to ignore/leave alone/commit/abort for junk files
- Shows file list before committing
- Offers to commit changes (with custom message)
- Checks if branch needs pushing
- Offers to push to origin
- Detects base branch (feature or develop) from git config
- Merges session branch into base branch (with AI-generated message)
- Switches back to base branch
- Shows session summary

**Example:**
```bash
$ ./scripts/end_dev_session.sh

🏁 Ending Development Session
================================

📋 Current branch: dev/session-20251115-200000

📋 Step 1: Checking for uncommitted changes and untracked files...
   ⚠️  You have changes:
   ?? IMPORTANT.md
   ?? junk.poo
   ?? scripts/wisdom.py
   🤖 Analyzing files with AI...

   📋 Files detected that should probably be ignored:
      - junk.poo
   What would you like to do with these files?
      [i] Ignore (add to .gitignore)
      [l] Leave alone (don't ignore, don't commit) [default]
      [c] Commit them anyway
      [a] Abort session end
   Choose (i/l/c/a) [default: l]: l
   ℹ️  Leaving files alone. They will remain untracked.

   📋 Files that will be committed:
   New files to add:
      A IMPORTANT.md
      A scripts/wisdom.py

   What would you like to do with these files?
      [c] Commit [default]
      [l] Leave alone (don't commit)
      [a] Abort session end
   Choose (c/l/a) [default: c]: 
   📝 Enter commit message (or press Enter for default):
   Default: feat: add Python module
   ✅ Changes committed

📋 Step 2: Checking branch status...
   📤 Pushing to origin (auto)...
   ✅ Pushed to origin

📋 Step 3: Session Summary
================================
   Branch: dev/session-20251115-200000
   Status: dev/session-20251115-200000...origin/dev/session-20251115-200000

📋 Step 4: Merge into base branch
   Base branch: feature/cursor-markdown-improvements
   Branch has 2 commit(s) to merge into feature/cursor-markdown-improvements
   Merge dev/session-20251115-200000 into feature/cursor-markdown-improvements? (Y/n): 
   🤖 Generating merge commit message with AI...
   Merging into feature/cursor-markdown-improvements...
   Merge message: Merge dev/session-20251115-200000: add resume script and improve file handling
   ✅ Merged dev/session-20251115-200000 into feature/cursor-markdown-improvements

📋 Step 5: Cleanup
   ✅ Already on feature/cursor-markdown-improvements (after merge)

✅ Development session ended!
```

## Complete Workflow Example

### Feature Branch Workflow

```bash
# 1. Start session from feature branch
./scripts/start_dev_session.sh cursor-markdown-improvements

# This creates:
# - feature/cursor-markdown-improvements (if doesn't exist)
# - dev/session-20251115-200000 (from feature branch)

# 2. Make your changes
vim src/processing/cursor/markdown_writer.py
# ... edit files ...

# 3. Test your changes
python -m pytest tests/

# 4. Commit as you go
git add .
git commit -m "feat: add global storage query support"

# 5. End session (merges back into feature branch)
./scripts/end_dev_session.sh

# 6. Later, merge feature branch into develop when ready
git checkout develop
git merge feature/cursor-markdown-improvements
```

### Direct Develop Workflow

```bash
# 1. Start session from develop (no feature branch)
./scripts/start_dev_session.sh

# This creates:
# - dev/session-20251115-200000 (from develop)

# 2. Make your changes and commit
# ... work ...

# 3. End session (merges back into develop)
./scripts/end_dev_session.sh
```

### Resuming a Session

```bash
# Resume most recent session (just press Enter)
./scripts/resume_dev_session.sh

# Or select a specific session
./scripts/resume_dev_session.sh
# [Select option 2 for older session]
```

## Best Practices

### ✅ DO

- **Use feature branches**: Create feature branches for larger work, use session branches for daily work
- **Start sessions properly**: Use `start_dev_session.sh` to ensure branches are synced
- **Session branches merge to feature**: When working on a feature, start session from feature branch
- **Commit frequently**: Commit logical units of work
- **End sessions cleanly**: Use `end_dev_session.sh` to ensure nothing is lost and merged properly
- **Push regularly**: Push your branches to origin for backup
- **Resume sessions**: Use `resume_dev_session.sh` to continue previous work

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

