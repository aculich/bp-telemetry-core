#!/bin/bash
# Start Development Session
# Standardized workflow for beginning a development session
#
# Usage:
#   ./scripts/start_dev_session.sh [feature-name]
#
# Options:
#   feature-name    Optional name for feature branch (default: auto-generated)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

FEATURE_NAME="${1:-}"

# Check if sync_upstream.sh exists (scripts should be on develop branch)
# Store the path before we potentially switch branches
SYNC_SCRIPT_PATH="$REPO_ROOT/scripts/sync_upstream.sh"
if [[ ! -f "$SYNC_SCRIPT_PATH" ]]; then
    echo "❌ Error: Workflow scripts not found."
    echo ""
    echo "These scripts are fork-specific and exist on the 'develop' branch."
    echo "Please checkout develop first:"
    echo "   git checkout develop"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "🚀 Starting Development Session"
echo "================================"
echo ""

# Step 1: Ensure we're on main and sync with upstream
echo "📋 Step 1: Syncing main with upstream..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [[ "$CURRENT_BRANCH" != "main" ]]; then
    echo "⚠️  Currently on '$CURRENT_BRANCH', switching to main..."
    git checkout main
    
    # After switching to main, check if sync script still exists
    # If not, we need to get it from develop temporarily or error out
    if [[ ! -f "$SYNC_SCRIPT_PATH" ]]; then
        echo "   ⚠️  sync_upstream.sh not found on main branch."
        echo "   Creating temporary reference from develop..."
        git show develop:scripts/sync_upstream.sh > "$SYNC_SCRIPT_PATH" 2>/dev/null || {
            echo "   ❌ Could not access sync_upstream.sh from develop branch."
            echo "   Please ensure you're running this from a branch that has access to develop."
            exit 1
        }
        chmod +x "$SYNC_SCRIPT_PATH"
    fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Warning: You have uncommitted changes on main."
    echo "   Stashing changes..."
    git stash push -m "Auto-stash before dev session start $(date +%Y-%m-%d-%H%M%S)"
fi

# Sync main with upstream (dry-run first to show what will happen)
echo "   Checking upstream sync status..."
SYNC_OUTPUT=$(./scripts/sync_upstream.sh --dry-run 2>&1)
if echo "$SYNC_OUTPUT" | grep -q "Already in sync"; then
    echo "   ✅ main is already in sync with upstream"
else
    # Check if there are commits to add (upstream ahead) vs commits to remove (local ahead)
    UPSTREAM_AHEAD=$(echo "$SYNC_OUTPUT" | grep -c "Commits that will be added" || echo "0")
    LOCAL_AHEAD=$(echo "$SYNC_OUTPUT" | grep -c "Commits that will be removed" || echo "0")
    
    if [[ "$UPSTREAM_AHEAD" -gt 0 ]]; then
        # Upstream has new commits - auto-sync (this is the normal case)
        echo "   ⚠️  main needs syncing with upstream (new commits available)."
        echo "   🔄 Syncing automatically..."
        ./scripts/sync_upstream.sh
    elif [[ "$LOCAL_AHEAD" -gt 0 ]]; then
        # Local has commits not in upstream - ask (might lose work)
        echo "   ⚠️  main has local commits not in upstream."
        echo "   ⚠️  Syncing will remove these commits from main."
        read -p "   Sync anyway? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ./scripts/sync_upstream.sh
        else
            echo "   ⚠️  Skipping sync. Make sure to sync before starting work!"
        fi
    else
        # Unknown state - ask
        echo "   ⚠️  main sync status unclear."
        read -p "   Sync now? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            ./scripts/sync_upstream.sh
        else
            echo "   ⚠️  Skipping sync. Make sure to sync before starting work!"
        fi
    fi
fi

# Step 2: Update develop with latest from main
echo ""
echo "📋 Step 2: Updating develop branch..."

# Clean up temporary sync script if it was created (untracked file)
if [[ -f "$SYNC_SCRIPT_PATH" ]] && ! git ls-files --error-unmatch "$SYNC_SCRIPT_PATH" >/dev/null 2>&1; then
    echo "   Cleaning up temporary sync script..."
    rm -f "$SYNC_SCRIPT_PATH"
fi

# Check if develop exists locally first
if git show-ref --verify --quiet refs/heads/develop; then
    # Branch exists locally, just checkout
    git checkout develop
elif git show-ref --verify --quiet refs/remotes/origin/develop; then
    # Branch exists on remote, create tracking branch
    echo "   ⚠️  develop branch doesn't exist locally. Creating from origin..."
    git fetch origin
    git checkout -b develop origin/develop
else
    # Branch doesn't exist anywhere, create new
    echo "   ⚠️  develop branch doesn't exist. Creating new develop branch..."
    git checkout -b develop
fi

# Merge main into develop to get latest upstream changes
echo "   Merging main into develop..."
if git merge main --no-edit --no-ff 2>&1 | grep -q "Already up to date"; then
    echo "   ✅ develop is already up to date with main"
else
    echo "   ✅ Merged latest changes from main into develop"
fi

# Step 3: Create or checkout development branch
echo ""
echo "📋 Step 3: Setting up development branch..."

if [[ -z "$FEATURE_NAME" ]]; then
    # Generate session name from timestamp
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    FEATURE_NAME="dev/session-${TIMESTAMP}"
    echo "   No session name provided, using: $FEATURE_NAME"
else
    # Allow both dev/ and feature/ prefixes, default to dev/ if no prefix
    if [[ "$FEATURE_NAME" =~ ^(dev/|feature/) ]]; then
        FEATURE_NAME="${FEATURE_NAME}"
    else
        FEATURE_NAME="dev/${FEATURE_NAME}"
    fi
    echo "   Using branch: $FEATURE_NAME"
fi

# Check if branch already exists
if git rev-parse --verify "$FEATURE_NAME" >/dev/null 2>&1; then
    # Check if we're already on this branch
    if [[ "$(git rev-parse --abbrev-ref HEAD)" == "$FEATURE_NAME" ]]; then
        echo "   ℹ️  Already on branch '$FEATURE_NAME'. Continuing..."
    else
        # Check if branch has uncommitted changes or unpushed commits
        git checkout "$FEATURE_NAME" >/dev/null 2>&1
        HAS_UNCOMMITTED=$(git diff-index --quiet HEAD --; echo $?)
        LOCAL_COMMITS=$(git rev-list --count origin/"$FEATURE_NAME"..HEAD 2>/dev/null || echo "0")
        git checkout develop >/dev/null 2>&1
        
        if [[ "$HAS_UNCOMMITTED" -eq 1 ]] || [[ "$LOCAL_COMMITS" -gt 0 ]]; then
            # Branch has work - auto-checkout (probably continuing previous session)
            echo "   ℹ️  Branch '$FEATURE_NAME' exists with work. Checking out..."
            git checkout "$FEATURE_NAME"
            echo "   ✅ Checked out existing branch"
        else
            # Branch exists but no work - ask
            echo "   ⚠️  Branch '$FEATURE_NAME' already exists (no uncommitted changes)."
            read -p "   Checkout existing branch? (Y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                git checkout "$FEATURE_NAME"
                echo "   ✅ Checked out existing branch"
            else
                echo "   ❌ Aborted. Please provide a different branch name."
                exit 1
            fi
        fi
    fi
else
    # Create new branch from develop
    git checkout -b "$FEATURE_NAME"
    echo "   ✅ Created and checked out branch: $FEATURE_NAME"
fi

# Step 4: Show status
echo ""
echo "📋 Step 4: Current Status"
echo "================================"
echo "   Current branch: $(git rev-parse --abbrev-ref HEAD)"
echo "   Upstream status:"
git status -sb | head -1
echo ""
echo "✅ Development session ready!"
echo ""
echo "Next steps:"
echo "   1. Make your changes"
echo "   2. Commit: git add . && git commit -m 'feat: your changes'"
echo "   3. Push: git push origin $FEATURE_NAME"
echo "   4. When done, run: ./scripts/end_dev_session.sh"
echo ""
echo "Branch naming convention:"
echo "   - dev/session-{timestamp} - Development sessions (auto-generated)"
echo "   - dev/{name} - Other development work"
echo "   - feature/{name} - Feature branches (use explicit 'feature/' prefix)"
echo ""

